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