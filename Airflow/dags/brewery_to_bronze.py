from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Permitir que o Airflow importe o script
sys.path.append("/usr/local/airflow/include/scripts") 
from brewery_api_ingestion import brewery_api

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "brewery_to_bronze",
    default_args=default_args,
    description="Coleta dados da API OpenBreweryDB e salva no MinIO",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    fetch_task = PythonOperator(
        task_id="brewery_api",
        python_callable=brewery_api,
    )

    fetch_task
