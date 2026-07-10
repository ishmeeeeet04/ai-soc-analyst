import pandas as pd

# Read the CSV file into a DataFrame
logs = pd.read_csv("data/raw/sample_logs.csv")

# Convert the timestamp column from plain text into an actual datetime object
# Why: right now, pandas sees "2024-01-15 09:05:47" as just a string of characters.
# Converting it lets us do time-based math (like "how many seconds apart are these?")
logs["timestamp"] = pd.to_datetime(logs["timestamp"])

print("=== All Logs ===")
print(logs)

# Filter: keep only rows where status is "failed"
failed_logins = logs[logs["status"] == "failed"]

print("\n=== Failed Login Attempts ===")
print(failed_logins)

# Group failed attempts by user, and count how many each user has
failed_counts = failed_logins.groupby("user").size()

print("\n=== Failed Login Count Per User ===")
print(failed_counts)

# Our rule: flag any user with 3 or more failed attempts
suspicious_users = failed_counts[failed_counts >= 3]

print("\n=== 🚨 SUSPICIOUS USERS (3+ failed logins) ===")
print(suspicious_users)