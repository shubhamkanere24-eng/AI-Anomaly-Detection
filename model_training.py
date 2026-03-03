import numpy as np

# Load sliding windows
X_train = np.load("data/sliding_windows.npy")  # shape: (num_windows, window_size, num_features)
X_train = X_train.reshape(X_train.shape[0], -1)  # Flatten each window to 1D (num_windows, 240)

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

input_dim = X_train.shape[1]  # 240
input_layer = Input(shape=(input_dim,))
encoded = Dense(128, activation='relu')(input_layer)
encoded = Dense(64, activation='relu')(encoded)
encoded = Dense(32, activation='relu')(encoded)
decoded = Dense(64, activation='relu')(encoded)
decoded = Dense(128, activation='relu')(decoded)
decoded = Dense(input_dim, activation='linear')(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)
autoencoder.compile(optimizer='adam', loss='mse')

# Train the autoencoder
history = autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=32,
    validation_split=0.1,
    shuffle=True
)

from sklearn.ensemble import IsolationForest

# Train Isolation Forest on same flattened data
iso_forest = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
iso_forest.fit(X_train)

# Decision function & predictions
scores = iso_forest.decision_function(X_train)  # Higher = more normal
preds = iso_forest.predict(X_train)            # 1 = normal, -1 = anomaly

# Reconstruct sequences
X_pred = autoencoder.predict(X_train)

# Mean Squared Error per sample
reconstruction_errors = np.mean(np.square(X_train - X_pred), axis=1)

# Threshold for anomaly detection (mean + 3*std)
threshold = np.mean(reconstruction_errors) + 3 * np.std(reconstruction_errors)
print("Reconstruction error threshold:", threshold)

# Flag anomalies
anomalies = reconstruction_errors > threshold
print("Number of anomalies detected:", np.sum(anomalies))
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Create models folder if missing
os.makedirs("models", exist_ok=True)

# Save autoencoder
autoencoder.save("models/autoencoder_model.keras")

# Save Isolation Forest
joblib.dump(iso_forest, "models/isolation_forest_model.pkl")

# If you already created scaler during Activity 2.3, load it
# If not, recreate it on scaled dataset
scaler = StandardScaler()
X_scaled_csv = np.load("data/sliding_windows.npy").reshape(-1, 240)
scaler.fit(X_scaled_csv)
joblib.dump(scaler, "models/scaler.pkl")