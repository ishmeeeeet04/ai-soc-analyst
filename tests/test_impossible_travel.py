import pandas as pd
from unittest.mock import patch
from src.detections.impossible_travel import detect_impossible_travel


def fake_location_lookup(ip):
    fake_locations = {
        "1.1.1.1": {"lat": 40.7128, "lon": -74.0060, "city": "New York", "country": "USA"},
        "2.2.2.2": {"lat": 52.5200, "lon": 13.4050, "city": "Berlin", "country": "Germany"},
    }
    return fake_locations.get(ip)


@patch("src.detections.impossible_travel.get_ip_location", side_effect=fake_location_lookup)
def test_detects_impossible_travel(mock_lookup):
    data = {
        "user": ["carol", "carol"],
        "source_ip": ["1.1.1.1", "2.2.2.2"],
        "status": ["success", "success"],
        "timestamp": pd.to_datetime(["2024-01-15 11:00:00", "2024-01-15 11:05:00"])
    }
    logs = pd.DataFrame(data)

    result = detect_impossible_travel(logs, max_speed_kmh=900)

    assert len(result) == 1
    assert result[0]["user"] == "carol"
    assert result[0]["mitre_technique_id"] == "T1078"


@patch("src.detections.impossible_travel.get_ip_location", side_effect=fake_location_lookup)
def test_does_not_flag_same_ip(mock_lookup):
    data = {
        "user": ["carol", "carol"],
        "source_ip": ["1.1.1.1", "1.1.1.1"],
        "status": ["success", "success"],
        "timestamp": pd.to_datetime(["2024-01-15 11:00:00", "2024-01-15 11:05:00"])
    }
    logs = pd.DataFrame(data)

    result = detect_impossible_travel(logs, max_speed_kmh=900)

    assert len(result) == 0