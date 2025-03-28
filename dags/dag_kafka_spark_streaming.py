from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

# Fonction pour lancer le script Python qui génère les données
def generate_data():
    subprocess.run(["python", "./script/gen_data.py"])

# Fonction pour lancer le traitement Spark
def start_spark_streaming():
    subprocess.run(["spark-submit", "./script/spark_streaming.py"])

# Définir le DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

dag = DAG(
    'kafka_spark_streaming',
    default_args=default_args,
    description='Test Kafka et Spark avec Airflow',
    schedule_interval='@once',  # Peut être modifié en fonction des besoins
)

# Définir les tâches
generate_data_task = PythonOperator(
    task_id='generate_data_task',
    python_callable=generate_data,
    dag=dag,
)

spark_streaming_task = PythonOperator(
    task_id='spark_streaming_task',
    python_callable=start_spark_streaming,
    dag=dag,
)

# Ordonner les tâches
generate_data_task >> spark_streaming_task
