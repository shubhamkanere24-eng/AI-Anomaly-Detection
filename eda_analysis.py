import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("data/healthcare_data.csv")

print("Dataset Shape:", df.shape)
print("\nBasic Info:")
print(df.info())

print("\nStatistical Summary:")
print(df.describe())

# -----------------------------
# 1️⃣ Distribution Plots
# -----------------------------

columns = ['heart_rate', 'blood_pressure', 'spo2', 'temperature']

for col in columns:
    plt.figure(figsize=(6,4))
    sns.histplot(df[col], bins=10, kde=True)
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.show()

# -----------------------------
# 2️⃣ Boxplots (Outlier Detection)
# -----------------------------

for col in columns:
    plt.figure(figsize=(6,4))
    sns.boxplot(x=df[col])
    plt.title(f"Boxplot of {col}")
    plt.show()

# -----------------------------
# 3️⃣ Correlation Heatmap
# -----------------------------

plt.figure(figsize=(6,5))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.show()