import pandas as pd

# Load dataset
df = pd.read_csv("healthcare_data.csv")

# 1. Dataset shape
print("Dataset Shape:", df.shape)

# 2. Column names
print("\nColumns:")
print(df.columns)

# 3. Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 4. Statistical summary
print("\nStatistical Summary:")
print(df.describe())

# 5. Dataset preview
print("\nDataset Preview:")
print(df.head())