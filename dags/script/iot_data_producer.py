from kafka import KafkaProducer
import psycopg2
import json
import time
import random
from datetime import datetime, timezone

# --- Configuration Kafka ---
KAFKA_BROKER = "broker:9092"
TOPIC = "iot_raw_data"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# --- Configuration PostgreSQL ---
PG_HOST = "iot_raw_database"
PG_PORT = 5432
PG_DB = "iot_raw_data"
PG_USER = "Polytech_agri"
PG_PASSWORD = "Polytech_agri"

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
    pressure FLOAT,
    latitude FLOAT,
    longitude FLOAT
);
""")
conn.commit()

# --- Définition des régions avec coordonnées GPS ---
REGIONS = {
    "DK": {"base_temp": 29, "base_humidity": 75, "lat": 14.7167, "lon": -17.4677},
    "TH": {"base_temp": 31, "base_humidity": 55, "lat": 14.7978, "lon": -16.9250},
    "TB": {"base_temp": 36, "base_humidity": 30, "lat": 15.3833, "lon": -15.5000},
    "MT": {"base_temp": 38, "base_humidity": 20, "lat": 16.0333, "lon": -13.5167},
    "ZG": {"base_temp": 28, "base_humidity": 85, "lat": 12.5833, "lon": -16.2667},
    "KD": {"base_temp": 32, "base_humidity": 60, "lat": 14.1167, "lon": -12.5000},
    "SL": {"base_temp": 30, "base_humidity": 60, "lat": 16.0167, "lon": -16.5000}
}

# Détermination de la saison
def get_season_name(month):
    if month in [7, 8, 9]:
        return "saison_des_pluies"
    elif month in [12, 1]:
        return "saison_fraiche"
    else:
        return "saison_seche"

# Génération des données simulées
def generate_raw_data():
    region = random.choice(list(REGIONS.keys()))
    climate = REGIONS[region]

    now = datetime.now(timezone.utc)
    month = now.month
    season = get_season_name(month)

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
        "pressure": pressure,
        "latitude": climate["lat"],
        "longitude": climate["lon"]
    }

# Insertion dans PostgreSQL
def insert_into_postgres(data):
    cursor.execute("""
        INSERT INTO iot_raw_data (
            machine_id, timestamp, region, season,
            temperature, humidity, soil_moisture,
            vibration, pressure, latitude, longitude
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        data["machine_id"],
        data["timestamp"],
        data["region"],
        data["season"],
        data["temperature"],
        data["humidity"],
        data["soil_moisture"],
        data["vibration"],
        data["pressure"],
        data["latitude"],
        data["longitude"]
    ))
    conn.commit()


if __name__ == "__main__":
    data = generate_raw_data()
    producer.send(TOPIC, value=data)
    insert_into_postgres(data)
    print(f"[{datetime.now(timezone.utc).isoformat()}] Donnée envoyée et stockée : {data}")
