from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Définition des arguments du DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,  # Ne pas dépendre des exécutions passées
    "retries": 1,  # Nombre de tentatives en cas d'échec
    "retry_delay": timedelta(minutes=5)  # Délai entre chaque tentative en cas d'échec
}

# Déclaration du DAG
with DAG(
    dag_id="iot_data_pipeline",  # Nom du DAG
    default_args=default_args,  # Arguments par défaut pour le DAG
    description="Génère des données IoT et les envoie vers Kafka + PostgreSQL",  # Description du DAG
    schedule_interval=timedelta(minutes=5),  # Exécution toutes les 5 minutes
    start_date=datetime(2024, 6, 1),  # Date de début
    catchup=False,  # Ne pas rattraper les exécutions manquées
    tags=["iot", "kafka", "postgres", "realtime"]  # Tags pour l'organisation du DAG
) as dag:

    # Définition de la tâche qui exécute le script iot_data_producer.py
    run_iot_producer = BashOperator(
        task_id="run_iot_producer_script",  # Nom de la tâche
        bash_command="python3 /opt/airflow/dags/script/iot_data_producer.py"  # Commande bash pour exécuter le script
    )

    # Définir les dépendances, ici il n'y en a qu'une seule tâche
    run_iot_producer
