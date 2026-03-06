from kafka import KafkaProducer
import time
import json
import random
import os
from dotenv import load_dotenv

# -------------------------------
# LOAD ENV VARIABLES
# -------------------------------
load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TOPIC")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Kafka Producer started...\n")

while True:

    vitals = {
        "patient_id": random.randint(1,5),
        "heart_rate": random.randint(60,120),
        "blood_pressure": random.randint(110,150),
        "temperature": round(random.uniform(36.5,39.0),1),
        "timestamp": time.time()
    }

    producer.send(TOPIC, value=vitals)

    print(f"Produced: {vitals}")

    time.sleep(1)