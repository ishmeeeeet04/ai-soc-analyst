from src.ingestion.read_logs import load_logs
from src.detections.brute_force import detect_brute_force
from src.detections.impossible_travel import detect_impossible_travel


def run_pipeline(filepath):
    """
    Loads logs and runs every detection rule against them.
    Input: filepath (string) - path to the raw log CSV
    Output: prints results of each detection to the terminal
    """
    logs = load_logs(filepath)

    print("=== All Logs ===")
    print(logs)

    brute_force_results = detect_brute_force(logs, threshold=3)
    print("\n=== 🚨 SUSPICIOUS USERS (Brute Force) ===")
    for result in brute_force_results:
        print(f"User: {result['user']} | Failed logins: {result['failed_login_count']} "
              f"| MITRE: {result['mitre_technique_id']} - {result['mitre_technique_name']}")

    travel_results = detect_impossible_travel(logs, max_speed_kmh=900)
    print("\n=== 🚨 SUSPICIOUS LOGINS (Impossible Travel) ===")
    for result in travel_results:
        print(f"User: {result['user']} | {result['first_location']} -> {result['second_location']} "
              f"| Speed: {result['required_speed_kmh']} km/h "
              f"| MITRE: {result['mitre_technique_id']} - {result['mitre_technique_name']}")


if __name__ == "__main__":
    run_pipeline("data/raw/synthetic_logs.csv")