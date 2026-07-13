import requests
import pandas as pd

logs = pd.read_csv("data/raw/synthetic_logs.csv")
logs["timestamp"] = logs["timestamp"].astype(str)

payload = logs.to_dict(orient="records")

response = requests.post("http://127.0.0.1:5000/analyze", json=payload)

print("Status Code:", response.status_code)

result = response.json()
print(f"\nRule-based brute force alerts: {len(result['rule_based']['brute_force_alerts'])}")
print(f"Rule-based impossible travel alerts: {len(result['rule_based']['impossible_travel_alerts'])}")
print(f"ML-flagged events: {result['summary']['total_ml_flagged_events']}")

print("\nFirst ML prediction example:")
if result['ml_based']['attack_predictions']:
    print(result['ml_based']['attack_predictions'][0])