from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, max as spark_max
import os
import json
import boto3
from datetime import datetime
import logging
import duckdb

# Caminho para o arquivo de credenciais
CREDENTIALS_PATH = os.getenv("MINIO_KEYS_FILE", "/usr/local/airflow/include/keys/minio_credentials.json")

def load_credentials(path=CREDENTIALS_PATH):
    with open(path, "r") as f:
        return json.load(f)

def import_silver_data(s3, bucket, prefix, local_path):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    parquet_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.parquet')]
    if not parquet_files:
        raise FileNotFoundError("Nenhum arquivo Parquet encontrado na camada silver.")

    for key in parquet_files:
        relative_path = os.path.relpath(key, prefix) 
        local_file = os.path.join(local_path, relative_path)
        os.makedirs(os.path.dirname(local_file), exist_ok=True)

        with open(local_file, "wb") as f:
            f.write(s3.get_object(Bucket=bucket, Key=key)['Body'].read())
        logging.info(f"Arquivo {key} baixado para {local_file}")

def main():
    # Carrega credenciais
    creds = load_credentials()
    endpoint = creds["endpoint"]
    access_key = creds["access_key"]
    secret_key = creds["secret_key"]
    bucket_silver = creds["bucket_silver"]
    prefix = creds["prefix"]
    bucket_gold = creds["bucket_gold"]

    silver_local_path = "/tmp/silver_data"
    duckdb_path = "/usr/local/airflow/include/minio.duckdb"
    output_file_name = "cervejarias.parquet"
    local_output_path = f"/tmp/{output_file_name}"
    s3_output_path = f"warehouse/{output_file_name}"

    # Cliente S3
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    import_silver_data(s3, bucket_silver, prefix, silver_local_path)

    # Spark
    spark = SparkSession.builder.appName("goldlayer").getOrCreate()
    df = spark.read.option("basePath", silver_local_path).parquet(silver_local_path)

    # Adiciona execution_time se não existir
    if 'execution_time' not in df.columns:
        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df = df.withColumn("execution_time", lit(execution_time))

    # Filtra pela última data
    latest_execution_time = df.select(spark_max("execution_time")).collect()[0][0]
    df_latest = df.filter(col("execution_time") == latest_execution_time)

    # Converte para pandas
    pandas_df = df_latest.toPandas()

    # DuckDB para agregação e exportação
    con = duckdb.connect(duckdb_path)
    con.register("pandas_df", pandas_df)

    # Agregação: cervejarias por tipo e localização
    con.execute("""
        CREATE OR REPLACE TABLE aggregated_breweries AS
        SELECT brewery_type, state_province, city, COUNT(*) AS total_cervejarias
        FROM pandas_df
        GROUP BY brewery_type, state_province, city
        ORDER BY total_cervejarias DESC
    """)

    # Exporta o resultado para Parquet
    con.execute(f"""
        COPY aggregated_breweries
        TO '{local_output_path}'
        (FORMAT PARQUET, OVERWRITE 1)
    """)

    # Upload para MinIO
    with open(local_output_path, 'rb') as f:
        s3.upload_fileobj(f, bucket_gold, s3_output_path)
        logging.info(f"Arquivo agregado enviado para s3://{bucket_gold}/{s3_output_path}")

if __name__ == "__main__":
    main()
