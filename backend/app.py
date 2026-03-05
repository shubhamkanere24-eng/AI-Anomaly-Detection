from flask import Flask, jsonify, request, render_template
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor, Json

app = Flask(__name__)

# -------------------------------
# PostgreSQL CONFIGURATION
# -------------------------------
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "ai_anomalies"
DB_USER = "postgres"
DB_PASSWORD = "$hubh@m123"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Connected to PostgreSQL successfully (Flask)")
except Exception as e:
    print("❌ PostgreSQL connection failed (Flask):", e)

# -------------------------------
# In-memory storage (fallback)
# -------------------------------
anomaly_logs = []  # All anomalies
patient_history = defaultdict(list)  # Patient-wise anomalies

# -------------------------------
# Helper function
# -------------------------------
def add_anomaly(anomaly):
    anomaly_logs.append(anomaly)
    patient_history[anomaly["patient_id"]].append(anomaly)

# -------------------------------
# API Endpoints
# -------------------------------
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/anomalies", methods=["GET"])
def get_anomalies():
    try:
        cursor.execute("SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT 1000;")
        rows = cursor.fetchall()
        # Convert JSONB vital_signs to normal dict and map risk_score to anomaly_score
        anomalies = []
        for row in rows:
            anomalies.append({
                "timestamp": row["timestamp"].timestamp() if row["timestamp"] else 0,
                "patient_id": row["patient_id"],
                "anomaly_score": row["severity"],
                "risk_score": row["severity"],
                "heart_rate": row["vital_signs"].get("Heart Rate",0),
                "blood_pressure": row["vital_signs"].get("Blood Pressure",0),
                "temperature": row["vital_signs"].get("Temperature",0),
                "explanations": [],  # Optional: keep empty for now
                "primary_contributor": ""
            })
        return jsonify(anomalies), 200
    except Exception as e:
        print("❌ Failed to fetch anomalies from PostgreSQL:", e)
        # fallback to in-memory
        return jsonify(anomaly_logs), 200

@app.route("/anomalies/<int:patient_id>", methods=["GET"])
def get_patient_history(patient_id):
    try:
        cursor.execute(
            "SELECT * FROM anomalies WHERE patient_id=%s ORDER BY timestamp DESC LIMIT 100;",
            (str(patient_id),)
        )
        rows = cursor.fetchall()
        if not rows:
            return jsonify({"message": f"No anomalies found for patient {patient_id}"}), 404
        anomalies = []
        for row in rows:
            anomalies.append({
                "timestamp": row["timestamp"].timestamp() if row["timestamp"] else 0,
                "patient_id": row["patient_id"],
                "anomaly_score": row["severity"],
                "risk_score": row["severity"],
                "heart_rate": row["vital_signs"].get("Heart Rate",0),
                "blood_pressure": row["vital_signs"].get("Blood Pressure",0),
                "temperature": row["vital_signs"].get("Temperature",0),
                "explanations": [],
                "primary_contributor": ""
            })
        return jsonify(anomalies), 200
    except Exception as e:
        print("❌ Failed to fetch patient history from PostgreSQL:", e)
        # fallback
        history = patient_history.get(patient_id, [])
        return jsonify(history), 200 if history else 404

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
    print("Flask backend running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)