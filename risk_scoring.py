import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib

# --- Step 1: Load models and scaler ---
autoencoder_model = tf.keras.models.load_model("models/autoencoder_model.keras")
iso_forest = joblib.load("models/isolation_forest_model.pkl")
scaler = joblib.load("models/scaler.pkl")  # optional, if you need original scaling

# --- Step 2: Load new data (or training data) ---
# Load new sliding window data
X_new = np.load("data/sliding_windows.npy")

# Reshape to match the autoencoder input
X_new = X_new.reshape(X_new.shape[0], autoencoder_model.input_shape[1])

# --- Step 3: Compute Autoencoder reconstruction error ---
X_pred = autoencoder_model.predict(X_new)
reconstruction_error = np.mean(np.square(X_new - X_pred), axis=1)

# --- Step 4: Compute Isolation Forest anomaly scores ---
iso_scores = -iso_forest.decision_function(X_new)  # higher = more anomalous

# --- Step 5: Normalize both scores ---
scaler_score = MinMaxScaler()
reconstruction_error_norm = scaler_score.fit_transform(reconstruction_error.reshape(-1,1)).flatten()
iso_scores_norm = scaler_score.fit_transform(iso_scores.reshape(-1,1)).flatten()

# --- Step 6: Combine into final risk score ---
final_risk_score = 0.5 * reconstruction_error_norm + 0.5 * iso_scores_norm

# --- Step 7: Classify severity ---
severity = []
for score in final_risk_score:
    if score < 0.33:
        severity.append("LOW")
    elif score < 0.66:
        severity.append("MEDIUM")
    else:
        severity.append("HIGH")

# --- Step 8: Save results to CSV ---
df_risk = pd.DataFrame({
    "risk_score": final_risk_score,
    "severity": severity
})

df_risk.to_csv("data/anomaly_risk_scores.csv", index=False)

# Optional: print first 10 results
for i, s in enumerate(severity[:10]):
    print(f"Sequence {i}: Risk score={final_risk_score[i]:.2f}, Severity={s}")