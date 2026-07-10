import pandas as pd
from unittest.mock import patch
from src.detections.impossible_travel import detect_impossible_travel


def fake_location_lookup(ip):
    """
    A fake replacement for get_ip_location(), so tests don't need real internet access.
    Returns fixed, known coordinates for two specific test IPs.
    """
    fake_locations = {
        "1.1.1.1": {"lat": 40.7128, "lon": -74.0060, "city": "New York", "country": "USA"},
        "2.2.2.2": {"lat": 52.5200, "lon": 13.4050, "city": "Berlin", "country": "Germany"},
    }
    return fake_locations.get(ip)


@patch("src.detections.impossible_travel.get_ip_location", side_effect=fake_location_lookup)
def test_detects_impossible_travel(mock_lookup):
    # Arrange: user logs in from New York, then Berlin, 5 minutes later
    data = {
        "user": ["carol", "carol"],
        "source_ip": ["1.1.1.1", "2.2.2.2"],
        "status": ["success", "success"],
        "timestamp": pd.to_datetime([
            "2024-01-15 11:00:00",
            "2024-01-15 11:05:00"
        ])
    }
    logs = pd.DataFrame(data)

    # Act
    result = detect_impossible_travel(logs, max_speed_kmh=900)

    # Assert: carol should be flagged, since NY-to-Berlin in 5 minutes is impossible
    assert len(result) == 1
    assert result.iloc[0]["user"] == "carol"


@patch("src.detections.impossible_travel.get_ip_location", side_effect=fake_location_lookup)
def test_does_not_flag_same_ip(mock_lookup):
    # Arrange: same IP used twice - no real travel happened
    data = {
        "user": ["carol", "carol"],
        "source_ip": ["1.1.1.1", "1.1.1.1"],
        "status": ["success", "success"],
        "timestamp": pd.to_datetime([
            "2024-01-15 11:00:00",
            "2024-01-15 11:05:00"
        ])
    }
    logs = pd.DataFrame(data)

    # Act
    result = detect_impossible_travel(logs, max_speed_kmh=900)

    # Assert: no flags, since IP didn't change
    assert len(result) == 0