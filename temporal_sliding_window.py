import pandas as pd
import numpy as np

# Load scaled vitals
df = pd.read_csv("data/scaled_healthcare_data.csv")

# Define window size (number of consecutive timesteps)
window_size = 5

# List of vital columns
vitals = df.columns.tolist()

# Create sliding windows
windows = []
for i in range(len(df) - window_size + 1):
    window = df[vitals].iloc[i:i+window_size].values
    windows.append(window)

# Convert to numpy array
windows = np.array(windows)

print(f"Sliding windows shape: {windows.shape}")  # (num_windows, window_size, num_features)

# Save sliding windows for later use
np.save("data/sliding_windows.npy", windows)