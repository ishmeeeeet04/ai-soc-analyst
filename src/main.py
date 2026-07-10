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
    print("\n=== 🚨 SUSPICIOUS USERS (Brute Force - 3+ failed logins) ===")
    print(brute_force_results)

    travel_results = detect_impossible_travel(logs, time_window_minutes=10)
    print("\n=== 🚨 SUSPICIOUS LOGINS (Impossible Travel) ===")
    print(travel_results)


if __name__ == "__main__":
    run_pipeline("data/raw/sample_logs.csv")