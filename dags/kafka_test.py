from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import json
import time

# Paramètres de connexion Kafka
KAFKA_BROKER = "broker:9092"  # Mets l'IP ou le hostname correct de ton broker Kafka
TOPIC = "airflow_kafka_test"

def produce_message():
    """Envoie un message de test à Kafka"""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    message = {"test": "Airflow → Kafka fonctionne !"}
    producer.send(TOPIC, message)
    producer.flush()
    print("Message envoyé à Kafka:", message)

def consume_message():
    """Consomme un message depuis Kafka et l'affiche"""
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000  # Timeout si aucun message reçu
    )

    print("En attente d'un message de Kafka...")
    for message in consumer:
        print("Message reçu de Kafka:", message.value)
        break  # On arrête après avoir reçu un message

# Définition du DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 3, 26),
    "retries": 1,
}

with DAG(
    dag_id="test_airflow_kafka",
    default_args=default_args,
    schedule_interval=None,  # Exécution manuelle
    catchup=False
) as dag:

    task_produce = PythonOperator(
        task_id="produce_message",
        python_callable=produce_message
    )

    task_consume = PythonOperator(
        task_id="consume_message",
        python_callable=consume_message
    )

    task_produce >> task_consume  # Exécute d'abord le producer, puis le consumer
