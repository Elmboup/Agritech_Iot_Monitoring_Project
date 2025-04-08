from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

def submit_spark_job():
    """Soumet un job Spark"""
    spark_submit_cmd = [
        "spark-submit",
        "--master", "spark://spark-master:7077",
        "/opt/airflow/dags/scripts/spark_job.py"
    ]

    result = subprocess.run(spark_submit_cmd, capture_output=True, text=True)
    print("Résultat du job Spark:", result.stdout)
    print("Erreurs éventuelles:", result.stderr)

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 3, 26),
    "retries": 1
}

with DAG(
    dag_id="test_airflow_spark",
    default_args=default_args,
    schedule_interval=None,  # Exécution manuelle
    catchup=False
) as dag:

    task_run_spark = PythonOperator(
        task_id="run_spark_job",
        python_callable=submit_spark_job
    )

task_run_spark
