from kafka import KafkaConsumer
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import defaultdict

TOPIC = "patient_vitals"

# Connect to Kafka
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='vitals-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer started and listening...\n")

# Store patient-wise sliding windows
patient_buffers = defaultdict(list)

# Store patient-wise models
patient_models = {}

WINDOW_SIZE = 30

for message in consumer:
    data = message.value
    patient_id = data['patient_id']

    print(f"\nReceived data for Patient {patient_id}: {data}")

    # Add vitals to sliding window
    patient_buffers[patient_id].append([
        data['heart_rate'],
        data['blood_pressure'],
        data['temperature']
    ])

    # Maintain window size
    if len(patient_buffers[patient_id]) > WINDOW_SIZE:
        patient_buffers[patient_id].pop(0)

    df = pd.DataFrame(
        patient_buffers[patient_id],
        columns=['heart_rate', 'blood_pressure', 'temperature']
    )

    # Create model for new patient
    if patient_id not in patient_models:
        patient_models[patient_id] = IsolationForest(contamination=0.1)

    # Train only when enough data
    if len(df) >= 10:
        model = patient_models[patient_id]
        model.fit(df)

        prediction = model.predict([[
            data['heart_rate'],
            data['blood_pressure'],
            data['temperature']
        ]])

        if prediction[0] == -1:
            print(f"🚨 Anomaly detected for Patient {patient_id}!")
        else:
            print(f"✅ Patient {patient_id} is Normal.")