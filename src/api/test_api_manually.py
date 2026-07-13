import requests
import pandas as pd

# Load our existing sample data and convert it to the JSON format our API expects
logs = pd.read_csv("data/raw/sample_logs.csv")

# Convert timestamp to string format for JSON (JSON doesn't have a native datetime type)
logs["timestamp"] = logs["timestamp"].astype(str)

# Convert the DataFrame into a list of dictionaries - exactly what our API expects
payload = logs.to_dict(orient="records")

# Send it to our running API
response = requests.post("http://127.0.0.1:5000/analyze", json=payload)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())