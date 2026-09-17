from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id="morocco_weather_pipeline",
    default_args=default_args,
    description="Automated 4-stage pipeline for Morocco weather risk monitoring",
    start_date=datetime(2026, 1 , 1),
    schedule="@daily",
    catchup=False,
) as dag:

    task_extract = BashOperator(
        task_id="extract_weather",
        bash_command="python /opt/airflow/src/extract.py"
    )

    task_silver = BashOperator(
        task_id="transform_silver",
        bash_command="python /opt/airflow/src/transform_silver.py"
    )

    task_gold = BashOperator(
        task_id="transform_gold",
        bash_command="python /opt/airflow/src/transform_gold.py"
    )

    task_load = BashOperator(
        task_id="load_postgres",
        bash_command="python /opt/airflow/src/load_postgres.py"
    )



task_extract >> task_silver >> task_gold >> task_load