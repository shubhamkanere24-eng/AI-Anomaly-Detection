from flask import Flask, jsonify, request
from collections import defaultdict
import time

app = Flask(__name__)

# -------------------------------
# In-memory storage for anomalies
# -------------------------------
anomaly_logs = []  # All anomalies
patient_history = defaultdict(list)  # Patient-wise anomalies

# -------------------------------
# Helper function to add anomaly
# -------------------------------
def add_anomaly(anomaly):
    """
    Adds an anomaly to storage.
    Expected keys in anomaly dict:
    - patient_id, heart_rate, blood_pressure, temperature, timestamp
    - anomaly_score, risk_score, explanations, primary_contributor
    """
    anomaly_logs.append(anomaly)
    patient_history[anomaly["patient_id"]].append(anomaly)

# -------------------------------
# API Endpoints
# -------------------------------

# 1️⃣ Fetch all anomalies
@app.route("/anomalies", methods=["GET"])
def get_anomalies():
    return jsonify(anomaly_logs), 200

# 2️⃣ Fetch patient-specific history
@app.route("/anomalies/<int:patient_id>", methods=["GET"])
def get_patient_history(patient_id):
    history = patient_history.get(patient_id, [])
    if not history:
        return jsonify({"message": f"No anomalies found for patient {patient_id}"}), 404
    return jsonify(history), 200

# 3️⃣ Fetch baseline vitals for a patient
@app.route("/baseline_vitals/<int:patient_id>", methods=["GET"])
def get_baseline_vitals(patient_id):
    history = patient_history.get(patient_id, [])
    if not history:
        return jsonify({"message": f"No data available for patient {patient_id}"}), 404
    baseline = {
        "heart_rate": sum(log["heart_rate"] for log in history)/len(history),
        "blood_pressure": sum(log["blood_pressure"] for log in history)/len(history),
        "temperature": sum(log["temperature"] for log in history)/len(history)
    }
    return jsonify(baseline), 200

# 4️⃣ POST endpoint to add anomaly (optional integration for consumer)
@app.route("/add_anomaly", methods=["POST"])
def post_anomaly():
    anomaly = request.get_json()
    if anomaly:
        add_anomaly(anomaly)
        return jsonify({"message": "Anomaly added"}), 201
    return jsonify({"message": "Invalid data"}), 400

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    print("Flask backend for AI Anomaly Detection running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)