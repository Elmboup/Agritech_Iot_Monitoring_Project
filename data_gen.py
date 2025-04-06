import time
import random
from elasticsearch import Elasticsearch
from regions import REGIONS

# Connexion à Elasticsearch avec authentification
es = Elasticsearch(
    "https://localhost:9200",  
    basic_auth=("elastic", "elastic"), #Authentification
    verify_certs=False
)

def generate_sensor_data():
    region = random.choice(REGIONS)
    climate = region["climate"]

    return {
        "machine_id": f'IOT-MACH-{region["prefixe"]}-{random.randint(1, 3)}',
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "region": region["nom"],
        "location" : {
            "lat": region["location"]["lat"],
            "lon" : region["location"]["lon"] 
        },
        "temperature": round(random.uniform(climate["temp_min"], climate["temp_max"]), 2),
        "humidity": round(random.uniform(climate["humidity_min"], climate["humidity_max"]), 2),
        "soil_humidity": round(random.uniform(10, 80), 2),  # Simule l'humidité du sol
        "vibration": round(random.uniform(0.1, 5.0), 2),  # Mesure machine
        "pressure": round(random.uniform(0.5, 2.5), 2),
        "status": random.choice(["Normal","Critique"])   # status enum : normal, alerte, critique
    }

# Envoi des données toutes les 5 secondes
while True:
    data = generate_sensor_data()
    es.index(index="sensors_data", document=data)  
    print(f"📡 Donnée envoyée : {data}")
    
    time.sleep(5)


# TODO # changer les position gps des capteurs au lieu de le fixer par region