from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

KAFKA_BROKER = "localhost:9092"
TOPIC = "iot_raw_data"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Données régionales
REGIONS = {
    "DK": {"temp_min": 25, "temp_max": 38, "humidity_min": 40, "humidity_max": 75},
    "TH": {"temp_min": 22, "temp_max": 35, "humidity_min": 35, "humidity_max": 70},
    "TB": {"temp_min": 20, "temp_max": 33, "humidity_min": 30, "humidity_max": 65},
    "MT": {"temp_min": 18, "temp_max": 30, "humidity_min": 25, "humidity_max": 60}
}

def generate_raw_data():
    region = random.choice(list(REGIONS.keys()))
    climate = REGIONS[region]

    return {
        "machine_id": f"IOT-MACH-{region}-{random.randint(1, 100)}",
        "timestamp": datetime.utcnow().isoformat(),
        "region": region,
        "temperature": round(random.uniform(climate["temp_min"], climate["temp_max"]), 2),
        "humidity": round(random.uniform(climate["humidity_min"], climate["humidity_max"]), 2),
        "soil_moisture": round(random.uniform(10, 80), 2),  # Simule l'humidité du sol
        "vibration": round(random.uniform(0.1, 5.0), 2),  # Mesure machine
        "pressure": round(random.uniform(0.5, 2.5), 2)
    }

while True:
    data = generate_raw_data()
    producer.send(TOPIC, value=data)
    print(f"Envoyé: {data}")
    time.sleep(2)
