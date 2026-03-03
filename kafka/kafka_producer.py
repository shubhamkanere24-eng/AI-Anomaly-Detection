from kafka import KafkaProducer
import time, json, random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    vitals = {
        "patient_id": random.randint(1,5),
        "heart_rate": random.randint(60,120),
        "blood_pressure": random.randint(110,150),
        "temperature": round(random.uniform(36.5,39.0),1),
        "timestamp": time.time()
    }
    producer.send('patient-vitals', value=vitals)
    print(f"Produced: {vitals}")
    time.sleep(1)