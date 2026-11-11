import pytest
from algorithms.deadlock import check_safety, handle_resource_request


def test_bankers_safety_algorithm_safe():
    # Silberschatz textbook example
    processes = ["P0", "P1", "P2", "P3", "P4"]
    available = [3, 3, 2]
    max_m = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]

    res = check_safety(processes, available, allocation, max_m)
    assert res["is_safe"] is True
    # Safe sequence exists and contains all 5 processes
    assert len(res["safe_sequence"]) == 5
    assert "P1" in res["safe_sequence"]


def test_bankers_resource_request_granted():
    processes = ["P0", "P1", "P2", "P3", "P4"]
    available = [3, 3, 2]
    max_m = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]

    # P1 requests [1, 0, 2]
    res = handle_resource_request(
        processes, available, allocation, max_m, "P1", [1, 0, 2]
    )
    assert res["granted"] is True


def test_bankers_resource_request_exceeds_need():
    processes = ["P0"]
    available = [10]
    max_m = [[5]]
    allocation = [[2]]
    # Need = 3. Requesting 4 exceeds maximum claim!
    res = handle_resource_request(processes, available, allocation, max_m, "P0", [4])
    assert res["granted"] is False
    assert "exceeded" in res["error"].lower()
