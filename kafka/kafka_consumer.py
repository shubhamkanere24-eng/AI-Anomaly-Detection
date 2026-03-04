from kafka import KafkaConsumer
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import defaultdict
import numpy as np

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
        patient_models[patient_id] = IsolationForest(
            contamination=0.1,
            random_state=42
        )

    # Train only when enough data
    if len(df) >= 10:
        model = patient_models[patient_id]
        model.fit(df)

        current_values = [[
            data['heart_rate'],
            data['blood_pressure'],
            data['temperature']
        ]]

        prediction = model.predict(current_values)
        anomaly_score = model.decision_function(current_values)[0]

        if prediction[0] == -1:

            # -----------------------------
            # EXPLAINABILITY LOGIC
            # -----------------------------
            explanations = []

            if data['heart_rate'] > 110:
                explanations.append("High Heart Rate")

            if data['temperature'] > 38:
                explanations.append("High Body Temperature")

            if data['blood_pressure'] > 140:
                explanations.append("High Blood Pressure")

            # Risk score (convert anomaly score to positive %)
            risk_score = abs(anomaly_score) * 100

            # Primary contributor
            vitals_dict = {
                "Heart Rate": data['heart_rate'],
                "Blood Pressure": data['blood_pressure'],
                "Temperature": data['temperature']
            }

            primary_contributor = max(vitals_dict, key=vitals_dict.get)

            # -----------------------------
            # ALERT OUTPUT
            # -----------------------------
            print("\n" + "="*50)
            print("🚨 CRITICAL HEALTH ANOMALY DETECTED 🚨")
            print("="*50)

            print(f"Patient ID      : {patient_id}")
            print(f"Anomaly Score   : {anomaly_score:.4f}")
            print(f"Risk Score      : {risk_score:.2f}%")

            print("\nAbnormal Factors:")
            if explanations:
                for exp in explanations:
                    print(f" - {exp}")
            else:
                print(" - Model detected anomaly pattern")

            print(f"\nPrimary Contributor: {primary_contributor}")
            print("="*50 + "\n")

        else:
            print(f"✅ Patient {patient_id} is Normal.")