from kafka import KafkaConsumer
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import defaultdict
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

import requests  # <-- Added for POSTing to Flask

TOPIC = "patient_vitals"

# -------------------------------
# MAILTRAP SMTP CONFIGURATION
# -------------------------------
SMTP_HOST = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 2525
SMTP_USERNAME = "9b1dc42ac93264"
SMTP_PASSWORD = "eef9162ee1a348"

SENDER_EMAIL = "alert@hospital.com"
RECEIVER_EMAIL = "doctor@hospital.com"

# -------------------------------
# Connect to Kafka
# -------------------------------
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='vitals-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer started and listening...\n")

# -------------------------------
# Data Storage
# -------------------------------
patient_buffers = defaultdict(list)
patient_models = {}

WINDOW_SIZE = 30

# Cooldown Logic
last_alert_time = {}
ALERT_COOLDOWN = 60  # seconds


# -------------------------------
# EMAIL FUNCTION
# -------------------------------
def send_email_alert(patient_id, data, anomaly_score, risk_score, explanations, primary_contributor):

    subject = "🚨 Critical Health Anomaly Detected"

    body = f"""
CRITICAL HEALTH ALERT

Patient ID: {patient_id}

Anomaly Score: {anomaly_score:.4f}
Risk Score: {risk_score:.2f}%

Vitals:
- Heart Rate: {data['heart_rate']}
- Blood Pressure: {data['blood_pressure']}
- Temperature: {data['temperature']}

Explainability:
{', '.join(explanations) if explanations else 'Model detected abnormal pattern'}

Primary Contributor:
{primary_contributor}

Immediate medical attention recommended.
"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("📧 Email alert sent successfully (Mailtrap)")
    except Exception as e:
        print("❌ Email failed:", e)


# -------------------------------
# MAIN CONSUMER LOOP
# -------------------------------
for message in consumer:
    data = message.value
    patient_id = data['patient_id']

    print(f"\nReceived data for Patient {patient_id}: {data}")

    patient_buffers[patient_id].append([
        data['heart_rate'],
        data['blood_pressure'],
        data['temperature']
    ])

    if len(patient_buffers[patient_id]) > WINDOW_SIZE:
        patient_buffers[patient_id].pop(0)

    df = pd.DataFrame(
        patient_buffers[patient_id],
        columns=['heart_rate', 'blood_pressure', 'temperature']
    )

    if patient_id not in patient_models:
        patient_models[patient_id] = IsolationForest(
            contamination=0.1,
            random_state=42
        )

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

            explanations = []

            if data['heart_rate'] > 110:
                explanations.append("High Heart Rate")

            if data['temperature'] > 38:
                explanations.append("High Body Temperature")

            if data['blood_pressure'] > 140:
                explanations.append("High Blood Pressure")

            risk_score = abs(anomaly_score) * 100

            vitals_dict = {
                "Heart Rate": data['heart_rate'],
                "Blood Pressure": data['blood_pressure'],
                "Temperature": data['temperature']
            }

            primary_contributor = max(vitals_dict, key=vitals_dict.get)

            current_time = time.time()

            if patient_id not in last_alert_time or \
               (current_time - last_alert_time[patient_id]) > ALERT_COOLDOWN:

                last_alert_time[patient_id] = current_time

                # -------------------------------
                # 1️⃣ Send Email
                # -------------------------------
                send_email_alert(
                    patient_id,
                    data,
                    anomaly_score,
                    risk_score,
                    explanations,
                    primary_contributor
                )

                # -------------------------------
                # 2️⃣ POST anomaly to Flask backend
                # -------------------------------
                anomaly_payload = {
                    "patient_id": patient_id,
                    "heart_rate": data['heart_rate'],
                    "blood_pressure": data['blood_pressure'],
                    "temperature": data['temperature'],
                    "timestamp": data['timestamp'],
                    "anomaly_score": anomaly_score,
                    "risk_score": risk_score,
                    "explanations": explanations,
                    "primary_contributor": primary_contributor
                }
                try:
                    requests.post(
                        "http://127.0.0.1:5000/add_anomaly",
                        json=anomaly_payload,
                        timeout=2
                    )
                except Exception as e:
                    print("❌ Failed to POST anomaly to Flask:", e)

                # -------------------------------
                # 3️⃣ Console logging
                # -------------------------------
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
                print("⚠ Cooldown active. Email not sent.")

        else:
            print(f"✅ Patient {patient_id} is Normal.")