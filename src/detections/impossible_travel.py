import pandas as pd
from src.detections.geo_utils import get_ip_location, calculate_distance_km


def detect_impossible_travel(logs, max_speed_kmh=900):
    """
    Flags users whose consecutive successful logins imply travel faster than
    max_speed_kmh (default 900 km/h, roughly the speed of a commercial flight).

    Input:
        logs (DataFrame) - the log data
        max_speed_kmh (int) - the maximum realistic travel speed, in km/h
    Output: a DataFrame listing suspicious login pairs with calculated speed
    """
    successful = logs[logs["status"] == "success"].copy()
    successful = successful.sort_values(by=["user", "timestamp"])

    suspicious_rows = []
    location_cache = {}  # avoids looking up the same IP twice - saves time and API calls

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
                continue  # same IP, no travel to check

            loc1 = get_cached_location(previous_login["source_ip"])
            loc2 = get_cached_location(current_login["source_ip"])

            if loc1 is None or loc2 is None:
                continue  # couldn't determine location, skip this pair

            distance_km = calculate_distance_km(loc1["lat"], loc1["lon"], loc2["lat"], loc2["lon"])

            time_diff = current_login["timestamp"] - previous_login["timestamp"]
            hours_apart = time_diff.total_seconds() / 3600

            if hours_apart == 0:
                required_speed = float("inf")  # same-instant logins from different places = infinite speed
            else:
                required_speed = distance_km / hours_apart

            if required_speed > max_speed_kmh:
                suspicious_rows.append({
                    "user": user,
                    "first_location": f"{loc1['city']}, {loc1['country']}",
                    "second_location": f"{loc2['city']}, {loc2['country']}",
                    "distance_km": round(distance_km, 1),
                    "hours_apart": round(hours_apart, 3),
                    "required_speed_kmh": round(required_speed, 1)
                })

    return pd.DataFrame(suspicious_rows)