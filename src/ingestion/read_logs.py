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


# This block only runs when we execute this file directly (not when imported elsewhere)
if __name__ == "__main__":
    logs = load_logs("data/raw/sample_logs.csv")
    print("=== All Logs ===")
    print(logs)

    suspicious = detect_brute_force(logs, threshold=3)
    print("\n=== 🚨 SUSPICIOUS USERS (3+ failed logins) ===")
    print(suspicious)