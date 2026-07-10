import pandas as pd


def engineer_features(logs):
    """
    Transforms raw log rows into a numeric feature table, one row per login event.
    Only uses information available BEFORE each event (no data leakage).

    Input: logs (DataFrame) - raw log data with columns:
           timestamp, source_ip, destination_ip, user, action, status
    Output: a new DataFrame with the original columns PLUS engineered numeric features
    """
    # Work on a copy so we never accidentally modify the original data
    logs = logs.copy()

    # Ensure timestamp is a real datetime (in case it wasn't already converted)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])

    # Sort chronologically per user - essential for correctly calculating "past" features
    logs = logs.sort_values(by=["user", "timestamp"]).reset_index(drop=True)

    # Feature 1: hour of day
    logs["hour_of_day"] = logs["timestamp"].dt.hour

    # Feature 2: is this specific login a failure?
    logs["is_failed"] = (logs["status"] == "failed").astype(int)

    # Prepare empty columns for the features we'll fill in row by row
    logs["failed_count_last_10min"] = 0
    logs["unique_ips_last_10min"] = 0
    logs["seconds_since_last_login"] = 0.0
    logs["is_new_ip_for_user"] = 0

    # We calculate rolling/history-based features per user, one user at a time
    for user, user_rows in logs.groupby("user"):
        seen_ips = set()  # tracks every IP we've seen so far for this user

        for idx, row in user_rows.iterrows():
            current_time = row["timestamp"]

            # Look only at THIS user's rows that happened strictly BEFORE the current one
            past_rows = user_rows[user_rows["timestamp"] < current_time]

            # Further narrow to only the last 10 minutes before this event
            window_start = current_time - pd.Timedelta(minutes=10)
            recent_rows = past_rows[past_rows["timestamp"] >= window_start]

            # Feature: how many failed logins in that recent window
            failed_count = (recent_rows["status"] == "failed").sum()
            logs.loc[idx, "failed_count_last_10min"] = failed_count

            # Feature: how many unique IPs used in that recent window
            unique_ips = recent_rows["source_ip"].nunique()
            logs.loc[idx, "unique_ips_last_10min"] = unique_ips

            # Feature: seconds since this user's previous login (any time in the past, not just 10min window)
            if len(past_rows) > 0:
                last_login_time = past_rows["timestamp"].max()
                seconds_gap = (current_time - last_login_time).total_seconds()
            else:
                seconds_gap = -1  # -1 signals "this is the user's first-ever login, no previous gap exists"
            logs.loc[idx, "seconds_since_last_login"] = seconds_gap

            # Feature: is this IP new for this user (never seen before THIS moment)?
            current_ip = row["source_ip"]
            logs.loc[idx, "is_new_ip_for_user"] = 0 if current_ip in seen_ips else 1
            seen_ips.add(current_ip)  # now mark it as seen, for future rows

    return logs