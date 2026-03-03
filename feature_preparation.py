import pandas as pd

# Load dataset
df = pd.read_csv("data/healthcare_data.csv")

# Rename blood_pressure to systolic_bp
df.rename(columns={"blood_pressure": "systolic_bp"}, inplace=True)

# -----------------------------------
# 1️⃣ Create Diastolic BP (Assumption)
# -----------------------------------
# Assume diastolic = systolic - 40 (approximation for demo)
df["diastolic_bp"] = df["systolic_bp"] - 40

# -----------------------------------
# 2️⃣ Add Respiratory Rate (Simulated)
# -----------------------------------
df["respiratory_rate"] = 16  # normal average

# -----------------------------------
# 3️⃣ Derived Feature: MAP
# MAP = (Systolic + 2*Diastolic) / 3
# -----------------------------------
df["MAP"] = (df["systolic_bp"] + 2 * df["diastolic_bp"]) / 3

# -----------------------------------
# 4️⃣ Derived Feature: HRV (Simplified)
# HRV simulated as small variation from heart rate
# -----------------------------------
df["HRV"] = df["heart_rate"] * 0.1

# -----------------------------------
# 5️⃣ Select Final Features
# -----------------------------------
features = [
    "heart_rate",
    "respiratory_rate",
    "temperature",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
    "HRV",
    "MAP"
]

df_final = df[features]

print("Final Feature Dataset:")
print(df_final.head())

# Save processed dataset
df_final.to_csv("data/processed_healthcare_data.csv", index=False)

print("\n✅ Feature preparation completed & saved.")