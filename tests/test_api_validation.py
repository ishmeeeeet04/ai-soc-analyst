import pytest
from src.api.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_analyze_rejects_invalid_json(client):
    response = client.post(
        "/analyze",
        data="not valid json{{{",
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_rejects_non_list_input(client):
    response = client.post(
        "/analyze",
        json={"not": "a list"}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_rejects_empty_list(client):
    response = client.post(
        "/analyze",
        json=[]
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_rejects_missing_required_fields(client):
    response = client.post(
        "/analyze",
        json=[{"foo": "bar"}]
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "missing" in response.get_json()["error"].lower()


def test_analyze_rejects_oversized_request(client):
    huge_input = [{"user": "test", "timestamp": "2026-01-01T00:00:00"} for _ in range(5001)]
    response = client.post(
        "/analyze",
        json=huge_input
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_health_check_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"