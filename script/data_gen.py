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

# DK: Dakar, TH: Thiès, TB: Touba, MT: Matam
REGIONS = {
    "DK": {"temp_min": 25, "temp_max": 38, "humidity_min": 40, "humidity_max": 75},
    "TH": {"temp_min": 22, "temp_max": 35, "humidity_min": 35, "humidity_max": 70},
    "TB": {"temp_min": 20, "temp_max": 33, "humidity_min": 30, "humidity_max": 65},
    "MT": {"temp_min": 18, "temp_max": 30, "humidity_min": 25, "humidity_max": 60}
}

# Saisons au Sénégal en fonction du mois
# - Saison sèche fraîche: Novembre à Mars
# - Saison sèche chaude: Avril à Juillet
# - Saison des pluies (hivernage): Juin à Octobre
def get_season_adjustments():
    current_month = datetime.now().month
    
    # Saison sèche fraîche
    if current_month in [11, 12, 1, 2, 3]:
        return {
            "temp_adjust": -4,  # Plus frais
            "humidity_adjust": -15,  # Plus sec
            "soil_moisture_adjust": -15,  # Sol plus sec
            "season_name": "Saison_Seche_Fraiche"
        }
    # Saison sèche chaude
    elif current_month in [ 4, 5, 6, 7]:
        return {
            "temp_adjust": +3,  # Plus chaud
            "humidity_adjust": -10,  # Très sec
            "soil_moisture_adjust": -20,  # Sol très sec
            "season_name": "Saison_Seche_Chaude"
        }
    # Saison des pluies (hivernage)
    else:  # 8, 9, 10
        return {
            "temp_adjust": 0,  # Température modérée
            "humidity_adjust": +20,  # Très humide
            "soil_moisture_adjust": +25,  # Sol humide/mouillé
            "season_name": "Hivernage"
        }

def generate_raw_data():
    region = random.choice(list(REGIONS.keys()))
    climate = REGIONS[region]
    season_adj = get_season_adjustments()
    
    # Appliquer les ajustements saisonniers
    temp_min = climate["temp_min"] + season_adj["temp_adjust"]
    temp_max = climate["temp_max"] + season_adj["temp_adjust"]
    
    humidity_min = max(10, climate["humidity_min"] + season_adj["humidity_adjust"])
    humidity_max = min(95, climate["humidity_max"] + season_adj["humidity_adjust"])
    
    soil_base = random.uniform(30, 50)  # Base d'humidité du sol
    soil_moisture = max(5, min(95, soil_base + season_adj["soil_moisture_adjust"]))
    
    return {
        "machine_id": f"IOT-MACH-{region}-{random.randint(1, 100)}",
        "timestamp": datetime.utcnow().isoformat(),
        "region": region,
        "season": season_adj["season_name"],
        "temperature": round(random.uniform(temp_min, temp_max), 2),
        "humidity": round(random.uniform(humidity_min, humidity_max), 2),
        "soil_moisture": round(soil_moisture + random.uniform(-5, 5), 2),
        "vibration": round(random.uniform(0.1, 5.0), 2),
        "pressure": round(random.uniform(0.5, 2.5), 2)
    }

while True:
    data = generate_raw_data()
    producer.send(TOPIC, value=data)
    print(f"Envoyé: {data}")
    time.sleep(2)