import pandas as pd
from src.detections.brute_force import detect_brute_force


def test_detects_user_with_enough_failed_logins():
    # Arrange: create a small fake dataset by hand, so we know EXACTLY what should happen
    data = {
        "user": ["alice", "alice", "alice", "bob"],
        "status": ["failed", "failed", "failed", "success"]
    }
    logs = pd.DataFrame(data)

    # Act: run the function we're testing
    result = detect_brute_force(logs, threshold=3)

    # Assert: alice should be flagged with exactly 3 failed attempts
    assert "alice" in result.index
    assert result["alice"] == 3


def test_does_not_flag_user_below_threshold():
    # Arrange: bob only has 2 failed logins, below our threshold of 3
    data = {
        "user": ["bob", "bob"],
        "status": ["failed", "failed"]
    }
    logs = pd.DataFrame(data)

    # Act
    result = detect_brute_force(logs, threshold=3)

    # Assert: bob should NOT appear in the results at all
    assert "bob" not in result.index


def test_empty_logs_return_empty_result():
    # Arrange: no logs at all
    logs = pd.DataFrame({"user": [], "status": []})

    # Act
    result = detect_brute_force(logs, threshold=3)

    # Assert: result should be empty, not crash
    assert len(result) == 0


def test_custom_threshold_works():
    # Arrange: alice has exactly 2 failures
    data = {
        "user": ["alice", "alice"],
        "status": ["failed", "failed"]
    }
    logs = pd.DataFrame(data)

    # Act: use a LOWER threshold of 2 instead of default 3
    result = detect_brute_force(logs, threshold=2)

    # Assert: with threshold=2, alice SHOULD now be flagged
    assert "alice" in result.index
    assert result["alice"] == 2