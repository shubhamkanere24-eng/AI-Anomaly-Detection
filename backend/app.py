from flask import Flask, jsonify, request
from collections import defaultdict
import time

app = Flask(__name__)

# In-memory storage
anomaly_logs = []
patient_history = defaultdict(list)

# Helper: add anomaly
def add_anomaly(anomaly):
    anomaly_logs.append(anomaly)
    patient_history[anomaly["patient_id"]].append(anomaly)

# GET all anomalies
@app.route("/anomalies", methods=["GET"])
def get_anomalies():
    return jsonify(anomaly_logs), 200

# GET patient-specific history
@app.route("/anomalies/<int:patient_id>", methods=["GET"])
def get_patient_history(patient_id):
    history = patient_history.get(patient_id, [])
    if not history:
        return jsonify({"message": f"No anomalies found for patient {patient_id}"}), 404
    return jsonify(history), 200

# GET baseline vitals
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

# POST add anomaly (for consumer)
@app.route("/add_anomaly", methods=["POST"])
def post_anomaly():
    anomaly = request.get_json()
    if anomaly:
        add_anomaly(anomaly)
        return jsonify({"message": "Anomaly added"}), 201
    return jsonify({"message": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)