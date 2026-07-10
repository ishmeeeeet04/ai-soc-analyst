import pandas as pd


def detect_impossible_travel(logs, time_window_minutes=10):
    """
    Flags users who logged in successfully from two different IP addresses
    within a short time window (a simplified impossible-travel check).

    Input:
        logs (DataFrame) - the log data
        time_window_minutes (int) - how close together (in minutes) two different-IP
                                     logins must be to count as suspicious
    Output: a DataFrame listing the suspicious login pairs
    """
    successful = logs[logs["status"] == "success"].copy()
    successful = successful.sort_values(by=["user", "timestamp"])

    suspicious_rows = []

    for user, user_logs in successful.groupby("user"):
        user_logs = user_logs.reset_index(drop=True)

        for i in range(1, len(user_logs)):
            previous_login = user_logs.iloc[i - 1]
            current_login = user_logs.iloc[i]

            time_diff = current_login["timestamp"] - previous_login["timestamp"]
            minutes_apart = time_diff.total_seconds() / 60

            different_ip = previous_login["source_ip"] != current_login["source_ip"]
            within_window = minutes_apart <= time_window_minutes

            if different_ip and within_window:
                suspicious_rows.append({
                    "user": user,
                    "first_ip": previous_login["source_ip"],
                    "first_time": previous_login["timestamp"],
                    "second_ip": current_login["source_ip"],
                    "second_time": current_login["timestamp"],
                    "minutes_apart": round(minutes_apart, 2)
                })

    return pd.DataFrame(suspicious_rows)