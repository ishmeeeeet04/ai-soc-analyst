from src.ingestion.read_logs import load_logs
from src.preprocessing.feature_engineering import engineer_features

logs = load_logs("data/raw/synthetic_logs.csv")
featured = engineer_features(logs)

# Show only the most relevant columns so it's easy to read
print(featured[[
    "timestamp", "user", "source_ip", "status",
    "hour_of_day", "is_failed", "failed_count_last_10min",
    "unique_ips_last_10min", "seconds_since_last_login", "is_new_ip_for_user"
]])