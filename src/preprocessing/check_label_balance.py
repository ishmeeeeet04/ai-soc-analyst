import pandas as pd

logs = pd.read_csv("data/raw/synthetic_logs.csv")
print(logs["is_attack"].value_counts())
print("\nPercentage breakdown:")
print(logs["is_attack"].value_counts(normalize=True) * 100)