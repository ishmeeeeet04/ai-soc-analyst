import pandas as pd
from src.detections.geo_utils import get_ip_location, calculate_distance_km
from src.detections.mitre_mapping import get_mitre_info


def detect_impossible_travel(logs, max_speed_kmh=900):
    """
    Flags users whose consecutive successful logins imply travel faster than
    max_speed_kmh. Returns results enriched with MITRE ATT&CK technique information.

    Input:
        logs (DataFrame) - the log data
        max_speed_kmh (int) - the maximum realistic travel speed, in km/h
    Output: a list of dictionaries, one per suspicious login pair, including MITRE context
    """
    successful = logs[logs["status"] == "success"].copy()
    successful = successful.sort_values(by=["user", "timestamp"])

    mitre_info = get_mitre_info("impossible_travel")
    suspicious_rows = []
    location_cache = {}

    def get_cached_location(ip):
        if ip not in location_cache:
            location_cache[ip] = get_ip_location(ip)
        return location_cache[ip]

    for user, user_logs in successful.groupby("user"):
        user_logs = user_logs.reset_index(drop=True)

        for i in range(1, len(user_logs)):
            previous_login = user_logs.iloc[i - 1]
            current_login = user_logs.iloc[i]

            if previous_login["source_ip"] == current_login["source_ip"]:
                continue

            loc1 = get_cached_location(previous_login["source_ip"])
            loc2 = get_cached_location(current_login["source_ip"])

            if loc1 is None or loc2 is None:
                continue

            distance_km = calculate_distance_km(loc1["lat"], loc1["lon"], loc2["lat"], loc2["lon"])
            time_diff = current_login["timestamp"] - previous_login["timestamp"]
            hours_apart = time_diff.total_seconds() / 3600

            if hours_apart == 0:
                required_speed = float("inf")
            else:
                required_speed = distance_km / hours_apart

            if required_speed > max_speed_kmh:
                suspicious_rows.append({
                    "user": user,
                    "first_location": f"{loc1['city']}, {loc1['country']}",
                    "second_location": f"{loc2['city']}, {loc2['country']}",
                    "distance_km": round(distance_km, 1),
                    "hours_apart": round(hours_apart, 3),
                    "required_speed_kmh": round(required_speed, 1),
                    "mitre_technique_id": mitre_info["technique_id"],
                    "mitre_technique_name": mitre_info["technique_name"],
                    "mitre_tactic": mitre_info["tactic"]
                })

    return suspicious_rows