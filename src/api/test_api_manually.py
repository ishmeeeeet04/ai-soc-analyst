import requests
import pandas as pd

logs = pd.read_csv("data/raw/synthetic_logs.csv")
logs["timestamp"] = logs["timestamp"].astype(str)

payload = logs.to_dict(orient="records")
response = requests.post("http://127.0.0.1:5000/analyze", json=payload)

result = response.json()
print("=== INCIDENT SUMMARY (LLM-Generated) ===")
print(result["incident_summary"])