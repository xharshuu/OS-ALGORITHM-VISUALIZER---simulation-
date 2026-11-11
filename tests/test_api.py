import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "OS Algorithm Visualizer" in data["app"]


def test_schedule_non_preemptive_api(client):
    payload = {
        "algorithm": "priority_non_preemptive",
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 4, "priority": 2},
            {"pid": "P2", "arrival": 1, "burst": 2, "priority": 1},
        ],
    }
    response = client.post("/api/schedule", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["algorithm"] == "priority_non_preemptive"
    assert "timeline" in data
    assert "processes" in data
    assert "metrics" in data
    assert data["metrics"]["total_burst_time"] == 6


def test_schedule_round_robin_api(client):
    payload = {
        "algorithm": "round_robin",
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 1},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
        ],
    }
    response = client.post("/api/schedule", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["algorithm"] == "round_robin"
    assert data["quantum"] == 2
    assert len(data["processes"]) == 2


def test_schedule_missing_quantum_round_robin(client):
    payload = {
        "algorithm": "round_robin",
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 1},
        ],
    }
    response = client.post("/api/schedule", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Time quantum is required" in data["error"]


def test_schedule_duplicate_pid(client):
    payload = {
        "algorithm": "priority_preemptive",
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 1},
            {"pid": "P1", "arrival": 2, "burst": 3, "priority": 2},
        ],
    }
    response = client.post("/api/schedule", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Duplicate Process ID 'P1'" in data["error"]


def test_compare_api(client):
    payload = {
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 4, "priority": 2},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 2, "burst": 2, "priority": 3},
        ],
    }
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "algorithms" in data
    assert "priority_non_preemptive" in data["algorithms"]
    assert "priority_preemptive" in data["algorithms"]
    assert "round_robin" in data["algorithms"]

    algos = data["algorithms"]
    assert algos["priority_non_preemptive"]["metrics"]["total_burst_time"] == 9
    assert algos["priority_preemptive"]["metrics"]["total_burst_time"] == 9
    assert algos["round_robin"]["metrics"]["total_burst_time"] == 9


def test_invalid_json_request(client):
    response = client.post("/api/schedule", data="not json", content_type="text/plain")
    assert response.status_code == 400
