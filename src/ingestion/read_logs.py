import pandas as pd


def load_logs(filepath):
    """
    Reads a CSV log file and converts its timestamp column to a proper datetime type.
    Input: filepath (string) - path to the CSV file
    Output: a pandas DataFrame with logs, ready for analysis
    """
    logs = pd.read_csv(filepath)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    return logs


def detect_brute_force(logs, threshold=3):
    """
    Flags users with 'threshold' or more failed login attempts.
    Input:
        logs (DataFrame) - the log data
        threshold (int) - minimum number of failures to be considered suspicious (default 3)
    Output: a pandas Series of usernames and their failed login counts, for suspicious users only
    """
    failed_logins = logs[logs["status"] == "failed"]
    failed_counts = failed_logins.groupby("user").size()
    suspicious_users = failed_counts[failed_counts >= threshold]
    return suspicious_users


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


if __name__ == "__main__":
    logs = load_logs("data/raw/sample_logs.csv")
    print("=== All Logs ===")
    print(logs)

    suspicious_brute_force = detect_brute_force(logs, threshold=3)
    print("\n=== 🚨 SUSPICIOUS USERS (Brute Force - 3+ failed logins) ===")
    print(suspicious_brute_force)

    suspicious_travel = detect_impossible_travel(logs, time_window_minutes=10)
    print("\n=== 🚨 SUSPICIOUS LOGINS (Impossible Travel) ===")
    print(suspicious_travel)