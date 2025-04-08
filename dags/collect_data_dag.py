from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import psycopg2
import json
import logging

# Configuration
KAFKA_BROKER = "kafka:9092"  # Utilisez le nom du service dans docker-compose
TOPIC = "iot_raw_data"
MAX_MESSAGES = 100  # Nombre maximum de messages à consommer par exécution

# Configuration PostgreSQL
PG_CONFIG = {
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
    "host": "postgres",
    "port": "5432"
}

def ensure_table_exists():
    """S'assurer que la table existe dans PostgreSQL"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iot_data (
                id SERIAL PRIMARY KEY,
                machine_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                region VARCHAR(10) NOT NULL,
                season VARCHAR(50) NOT NULL,
                temperature FLOAT NOT NULL,
                humidity FLOAT NOT NULL,
                soil_moisture FLOAT NOT NULL,
                vibration FLOAT NOT NULL,
                pressure FLOAT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Table iot_data vérifiée/créée avec succès")
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la vérification/création de la table: {e}")
        return False

def consume_data_from_kafka():
    """Consommer un nombre limité de messages depuis Kafka"""
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            group_id='iot_consumer_group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=30000  # Timeout après 30 secondes sans message
        )
        
        # S'assurer que la table existe
        if not ensure_table_exists():
            logging.error("Impossible de créer la table. Arrêt de la tâche.")
            return
        
        # Établir une connexion à PostgreSQL
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Compteurs
        messages_count = 0
        inserted_count = 0
        
        # Consommer les messages
        for message in consumer:
            data = message.value
            logging.info(f"Message consommé: {data['machine_id']}")
            
            try:
                # Insertion des données
                cursor.execute("""
                    INSERT INTO iot_data (machine_id, timestamp, region, season, temperature, 
                                          humidity, soil_moisture, vibration, pressure)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['machine_id'],
                    data['timestamp'],
                    data['region'],
                    data['season'],
                    data['temperature'],
                    data['humidity'],
                    data['soil_moisture'],
                    data['vibration'],
                    data['pressure']
                ))
                inserted_count += 1
            except Exception as e:
                logging.error(f"Erreur lors de l'insertion: {e}")
                # Continuer malgré l'erreur
            
            messages_count += 1
            
            # Limiter le nombre de messages par exécution
            if messages_count >= MAX_MESSAGES:
                break
        
        # Valider les changements et fermer les connexions
        conn.commit()
        cursor.close()
        conn.close()
        consumer.close()
        
        logging.info(f"Traitement terminé. {inserted_count}/{messages_count} messages insérés.")
        return f"Traitement terminé. {inserted_count}/{messages_count} messages insérés."
        
    except Exception as e:
        logging.error(f"Erreur lors de la consommation des données: {e}")
        return f"Erreur: {str(e)}"

# Définir le DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    'kafka_to_postgres',
    default_args=default_args,
    description='Consommer des données Kafka et les insérer dans PostgreSQL',
    schedule_interval='*/15 * * * *',  # Exécution toutes les 15 minutes
    catchup=False,
) as dag:

    # Tâche pour consommer les données et les insérer dans PostgreSQL
    consume_data_task = PythonOperator(
        task_id='consume_data_task',
        python_callable=consume_data_from_kafka,
    )