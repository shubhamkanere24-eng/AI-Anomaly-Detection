from kafka import KafkaConsumer
import json
import pandas as pd
from sklearn.ensemble import IsolationForest

consumer = KafkaConsumer(
    'patient-vitals',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

model = IsolationForest(contamination=0.1)
buffer = []

for message in consumer:
    data = message.value
    print(f"Consumed: {data}")

    buffer.append([data['heart_rate'], data['blood_pressure'], data['temperature']])
    if len(buffer) > 50:
        buffer.pop(0)

    df = pd.DataFrame(buffer, columns=['heart_rate', 'blood_pressure', 'temperature'])
    
    if len(df) >= 10:
        model.fit(df)
        pred = model.predict([[data['heart_rate'], data['blood_pressure'], data['temperature']]])
        if pred[0] == -1:
            print(f"Anomaly detected for patient {data['patient_id']}!")