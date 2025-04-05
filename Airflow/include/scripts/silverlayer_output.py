# O script tem como objetivo transformar os dados para um formato de armazenamento colunar Parquet, 
# e particionar por localização da cervejaria. 


from pyspark.sql import SparkSession
from pyspark.sql.functions import trim, col, lit
import os
import json
import boto3
from datetime import datetime
import logging

# Caminho para o arquivo de credenciais
CREDENTIALS_PATH = os.getenv("MINIO_KEYS_FILE", "/usr/local/airflow/include/keys/minio_credentials.json")

# Carrega as chaves
def load_credentials(path=CREDENTIALS_PATH):
    with open(path, "r") as f:
        return json.load(f)

# Buscar o arquivo json com a ultima data no bucket
def get_latest_json_file(s3, bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.json')]
    if not files:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado no bucket.")
    latest_file = sorted(files)[-1]
    logging.info(f"Último arquivo encontrado: {latest_file}")
    return latest_file

# Escrita dos dados em parquet, particionado por país.
def main():
    # Carrega credenciais do MinIO
    creds = load_credentials()
    endpoint = creds["endpoint"]
    access_key = creds["access_key"]
    secret_key = creds["secret_key"]
    bucket_bronze = creds["bucket_bronze"]
    bucket_silver = creds["bucket_silver"]
    prefix = creds["prefix"]

    # Cria cliente MinIO via boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    latest_file_key = get_latest_json_file(s3, bucket_bronze, prefix)
    response = s3.get_object(Bucket=bucket_bronze, Key=latest_file_key)
    content = response['Body'].read().decode('utf-8')

    temp_input_path = "/tmp/latest_brewery.json"
    with open(temp_input_path, "w") as f:
        f.write(content)

    # Inicia sessão spark
    spark = SparkSession.builder.appName("silverlayer").getOrCreate()

    # Leitura dos arquivos json e criação do df
    df = spark.read.option("multiline", "true").option("encoding", "UTF-8").json(temp_input_path)

    # Remove espaços em branco das colunas
    df = df.select([trim(col(c)).alias(c) if dtype == "string" else col(c) for c, dtype in df.dtypes])

    # Adiciona a coluna execution_time com o timestamp atual
    execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = df.withColumn("execution_time", lit(execution_time))

    output_path = f"/tmp/silver_output"

    df.write.partitionBy("country").parquet(output_path, mode="overwrite")

    # Envia os arquivos particionados para o MinIO
    for root, _, files in os.walk(output_path):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, output_path)
            key = os.path.join(prefix, relative_path).replace("\\", "/")
            with open(full_path, "rb") as f:
                s3.put_object(
                    Bucket=bucket_silver,
                    Key=key,
                    Body=f.read(),
                    ContentType="application/octet-stream"
                )
            logging.info(f"Arquivo salvo em: s3://{bucket_silver}/{key}")

if __name__ == "__main__":
    main()


