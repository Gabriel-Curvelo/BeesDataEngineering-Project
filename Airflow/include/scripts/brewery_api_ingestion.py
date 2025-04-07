# This script aims to persist raw data from the https://www.openbrewerydb.org API
# into the bronze layer of our data lake model. The generated files are saved in JSON format.

import os
import json
import requests
import boto3
import logging
from datetime import datetime

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the credentials file
CREDENTIALS_PATH = os.getenv("MINIO_KEYS_FILE", "/usr/local/airflow/include/keys/minio_credentials.json")

# Load keys
def load_credentials(path=CREDENTIALS_PATH):
    with open(path, "r") as f:
        return json.load(f)

# Paginated API request
def brewery_api():
    all_data = []
    page = 1
    per_page = 50

    while True:
        url = f"https://api.openbrewerydb.org/v1/breweries?page={page}&per_page={per_page}"
        logger.info(f"Requesting page {page}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.info("No data returned. End of pagination.")
            break

        all_data.extend(data)
        page += 1

    # Load MinIO credentials
    creds = load_credentials()
    endpoint = creds["endpoint"]
    access_key = creds["access_key"]
    secret_key = creds["secret_key"]
    bucket_bronze = creds["bucket_bronze"]
    prefix = creds["prefix"]

    # Generate file name based on timestamp
    filename = f"{prefix}brewery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Create MinIO client via boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Save JSON to the bucket
    s3.put_object(
        Bucket=bucket_bronze,
        Key=filename,
        Body=json.dumps(all_data),
        ContentType="application/json"
    )

    logger.info(f"File saved to: s3://{bucket_bronze}/{filename}")
    logger.info(f"Total records saved: {len(all_data)}")

# Direct execution (or via Airflow)
if __name__ == "__main__":
    brewery_api()
