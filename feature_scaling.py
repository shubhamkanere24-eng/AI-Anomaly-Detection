import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load processed dataset
df = pd.read_csv("data/processed_healthcare_data.csv")

# List of vital features (matching actual CSV column names)
vital_columns = [
    "heart_rate",
    "respiratory_rate",
    "temperature",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
    "HRV",
    "MAP"
]

# Select vital features
df_vitals = df[vital_columns]

# Initialize scaler
scaler = StandardScaler()

# Fit and transform
scaled_vitals = scaler.fit_transform(df_vitals)

# Convert to DataFrame
df_scaled = pd.DataFrame(scaled_vitals, columns=vital_columns)

# Save scaled dataset
df_scaled.to_csv("data/scaled_healthcare_data.csv", index=False)

print("Scaling completed successfully.")
print(df_scaled.head())