from src.detections.brute_force import detect_brute_force
import pandas as pd


def test_detects_user_with_enough_failed_logins():
    data = {
        "user": ["alice", "alice", "alice", "bob"],
        "status": ["failed", "failed", "failed", "success"]
    }
    logs = pd.DataFrame(data)

    result = detect_brute_force(logs, threshold=3)

    assert len(result) == 1
    assert result[0]["user"] == "alice"
    assert result[0]["failed_login_count"] == 3
    assert result[0]["mitre_technique_id"] == "T1110"


def test_does_not_flag_user_below_threshold():
    data = {
        "user": ["bob", "bob"],
        "status": ["failed", "failed"]
    }
    logs = pd.DataFrame(data)

    result = detect_brute_force(logs, threshold=3)

    assert len(result) == 0


def test_empty_logs_return_empty_result():
    logs = pd.DataFrame({"user": [], "status": []})

    result = detect_brute_force(logs, threshold=3)

    assert len(result) == 0


def test_custom_threshold_works():
    data = {
        "user": ["alice", "alice"],
        "status": ["failed", "failed"]
    }
    logs = pd.DataFrame(data)

    result = detect_brute_force(logs, threshold=2)

    assert len(result) == 1
    assert result[0]["user"] == "alice"
    assert result[0]["failed_login_count"] == 2