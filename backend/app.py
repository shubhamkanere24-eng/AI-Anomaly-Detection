from flask import Flask, jsonify, request, render_template
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# -------------------------------
# LOAD ENV VARIABLES
# -------------------------------
load_dotenv()

app = Flask(__name__)

# -------------------------------
# PostgreSQL CONFIGURATION
# -------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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
# In-memory fallback
# -------------------------------
anomaly_logs = []
patient_history = defaultdict(list)

# -------------------------------
# Helper
# -------------------------------
def add_anomaly(anomaly):

    anomaly_logs.append(anomaly)
    patient_history[anomaly["patient_id"]].append(anomaly)

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/anomalies", methods=["GET"])
def get_anomalies():

    try:

        cursor.execute(
            "SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT 1000;"
        )

        rows = cursor.fetchall()

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

        print("❌ Failed to fetch anomalies:", e)

        return jsonify(anomaly_logs), 200


@app.route("/add_anomaly", methods=["POST"])
def post_anomaly():

    anomaly = request.get_json()

    if anomaly:

        add_anomaly(anomaly)

        return jsonify({"message": "Anomaly added"}), 201

    return jsonify({"message": "Invalid data"}), 400


# -------------------------------
# RUN FLASK
# -------------------------------
if __name__ == "__main__":

    print("Flask backend running")

    app.run(
        host=os.getenv("FLASK_HOST"),
        port=int(os.getenv("FLASK_PORT")),
        debug=os.getenv("FLASK_DEBUG") == "True"
    )