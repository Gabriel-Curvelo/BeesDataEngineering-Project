
# Esse script tem como objetivo persistir os dados brutos da api https://www.openbrewerydb.org, 
# na camada bronze do nosso modelo de data lake. Os arquivos gerados são salvos em formato json.

import os
import json
import requests
import boto3
import logging
from datetime import datetime

# Configuração do logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho para o arquivo de credenciais
CREDENTIALS_PATH = os.getenv("MINIO_KEYS_FILE", "/usr/local/airflow/include/keys/minio_credentials.json")

# Carrega as chaves
def load_credentials(path=CREDENTIALS_PATH):
    with open(path, "r") as f:
        return json.load(f)

# Leitura da API com paginação
def brewery_api():
    all_data = []
    page = 1
    per_page = 50

    while True:
        url = f"https://api.openbrewerydb.org/v1/breweries?page={page}&per_page={per_page}"
        logger.info(f"🔄 Requisitando página {page}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.info("Nenhum dado retornado. Fim da paginação.")
            break

        all_data.extend(data)
        page += 1

    # Carrega credenciais do MinIO
    creds = load_credentials()
    endpoint = creds["endpoint"]
    access_key = creds["access_key"]
    secret_key = creds["secret_key"]
    bucket = creds["bucket"]
    prefix = creds["prefix"]

    # Gera nome do arquivo baseado no timestamp
    filename = f"{prefix}brewery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Cria cliente MinIO via boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Salva o JSON no bucket
    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=json.dumps(all_data),
        ContentType="application/json"
    )

    logger.info(f"Arquivo salvo em: s3://{bucket}/{filename}")
    logger.info(f"Total de registros salvos: {len(all_data)}")

# Execução direta (ou via Airflow)
if __name__ == "__main__":
    brewery_api()

