from kafka import KafkaProducer
import psycopg2
import json
import time
import random
from datetime import datetime

# --- Configuration Kafka ---
KAFKA_BROKER = "localhost:9092"
TOPIC = "iot_raw_data"

# Initialisation du producteur Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# --- Configuration PostgreSQL ---
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "iot_data"
PG_USER = "postgres"
PG_PASSWORD = "password"

# Connexion à PostgreSQL
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD
)
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS iot_raw_data (
    id SERIAL PRIMARY KEY,
    machine_id TEXT,
    timestamp TIMESTAMPTZ,
    region TEXT,
    season TEXT,
    temperature FLOAT,
    humidity FLOAT,
    soil_moisture FLOAT,
    vibration FLOAT,
    pressure FLOAT
);
""")
conn.commit()

# --- Définition des régions et du climat par saison ---
REGIONS = {
    "DK": {"base_temp": 29, "base_humidity": 75},
    "TH": {"base_temp": 31, "base_humidity": 55},
    "TB": {"base_temp": 36, "base_humidity": 30},
    "MT": {"base_temp": 38, "base_humidity": 20},
    "ZG": {"base_temp": 28, "base_humidity": 85},
    "KD": {"base_temp": 32, "base_humidity": 60},
    "SL": {"base_temp": 30, "base_humidity": 60}
}

def get_season_name(month):
    if month in [7, 8, 9]:
        return "saison_des_pluies"
    elif month in [12, 1]:
        return "saison_fraiche"
    else:
        return "saison_seche"

# Génération de données simulées
def generate_raw_data():
    region = random.choice(list(REGIONS.keys()))
    climate = REGIONS[region]
    
    now = datetime.utcnow()
    month = now.month
    season = get_season_name(month)

    # Ajustement climatique par saison
    temp_variation = {
        "saison_des_pluies": random.uniform(-1, 2),
        "saison_fraiche": random.uniform(-3, 0),
        "saison_seche": random.uniform(0, 2)
    }

    humidity_variation = {
        "saison_des_pluies": random.uniform(5, 15),
        "saison_fraiche": random.uniform(-5, 0),
        "saison_seche": random.uniform(-10, -2)
    }

    temperature = round(climate["base_temp"] + temp_variation[season], 2)
    humidity = round(climate["base_humidity"] + humidity_variation[season], 2)
    soil_moisture = round(random.uniform(30, 90) if season == "saison_des_pluies" else random.uniform(10, 50), 2)
    vibration = round(random.uniform(0.1, 5.0), 2)
    pressure = round(random.uniform(0.8, 2.5), 2)

    return {
        "machine_id": f"IOT-MACH-{region}-{random.randint(1, 100)}",
        "timestamp": now.isoformat(),
        "region": region,
        "season": season,
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "vibration": vibration,
        "pressure": pressure
    }

# Insertion dans la base PostgreSQL
def insert_into_postgres(data):
    cursor.execute("""
        INSERT INTO iot_raw_data (
            machine_id, timestamp, region, season,
            temperature, humidity, soil_moisture, vibration, pressure
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        data["machine_id"],
        data["timestamp"],
        data["region"],
        data["season"],
        data["temperature"],
        data["humidity"],
        data["soil_moisture"],
        data["vibration"],
        data["pressure"]
    ))
    conn.commit()

# --- Exécution principale ---
if __name__ == "__main__":
    print(" Démarrage de la génération et diffusion des données IoT...")

    while True:
        data = generate_raw_data()

        # Envoi vers Kafka
        producer.send(TOPIC, value=data)

        # Insertion dans PostgreSQL
        insert_into_postgres(data)

        print(f" Donnée envoyée et stockée: {data}")
        time.sleep(2)
