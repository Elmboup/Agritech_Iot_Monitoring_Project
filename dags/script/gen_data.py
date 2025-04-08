from kafka import KafkaProducer
import json
import random
import time

# Configuration du producteur Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Adresse de ton broker Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Sérialisation JSON
)

# Liste d'exemples de noms et âges
names = ["Alice", "Bob", "Charlie", "David", "Eve"]

def generate_data():
    """Génère un message aléatoire avec un nom et un âge."""
    name = random.choice(names)
    age = random.randint(18, 65)
    return {"name": name, "age": age}

# Envoi des données à Kafka toutes les 2 secondes
while True:
    data = generate_data()
    producer.send('test_topic', value=data)
    print(f"Envoyé: {data}")
    time.sleep(2)  # Simulation du streaming en envoyant des données à intervalles réguliers
