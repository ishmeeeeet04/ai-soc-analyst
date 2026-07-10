from src.detections.mitre_mapping import get_mitre_info


def detect_brute_force(logs, threshold=3):
    """
    Flags users with 'threshold' or more failed login attempts.
    Returns results enriched with MITRE ATT&CK technique information.

    Input:
        logs (DataFrame) - the log data
        threshold (int) - minimum number of failures to be considered suspicious (default 3)
    Output: a list of dictionaries, one per suspicious user, including MITRE context
    """
    failed_logins = logs[logs["status"] == "failed"]
    failed_counts = failed_logins.groupby("user").size()
    suspicious_users = failed_counts[failed_counts >= threshold]

    mitre_info = get_mitre_info("brute_force")

    results = []
    for user, count in suspicious_users.items():
        results.append({
            "user": user,
            "failed_login_count": int(count),
            "mitre_technique_id": mitre_info["technique_id"],
            "mitre_technique_name": mitre_info["technique_name"],
            "mitre_tactic": mitre_info["tactic"]
        })

    return results