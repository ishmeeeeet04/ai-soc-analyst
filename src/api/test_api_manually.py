import requests
import pandas as pd

logs = pd.read_csv("data/raw/synthetic_logs.csv")
logs["timestamp"] = logs["timestamp"].astype(str)

payload = logs.to_dict(orient="records")
response = requests.post("http://127.0.0.1:5000/analyze", json=payload)

print("Status Code:", response.status_code)
print("Raw Response Text:")
print(response.text)