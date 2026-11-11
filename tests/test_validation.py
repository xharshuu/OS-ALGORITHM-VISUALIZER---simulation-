import pytest
from algorithms.validation import (
    ValidationError,
    validate_processes,
    validate_quantum,
    validate_schedule_request,
)


def test_validate_processes_success():
    raw = [
        {"pid": "P1", "arrival": 0, "burst": 5, "priority": 1},
        {"pid": "P2", "arrival": "2", "burst": "3", "priority": "2"},
    ]
    validated = validate_processes(raw)
    assert len(validated) == 2
    assert validated[0]["pid"] == "P1"
    assert validated[0]["arrival"] == 0
    assert validated[0]["burst"] == 5
    assert validated[0]["priority"] == 1
    assert validated[1]["pid"] == "P2"
    assert validated[1]["arrival"] == 2
    assert validated[1]["burst"] == 3
    assert validated[1]["priority"] == 2


def test_empty_process_list():
    with pytest.raises(ValidationError) as exc:
        validate_processes([])
    assert "At least one process is required" in str(exc.value)


def test_duplicate_pid():
    raw = [
        {"pid": "P1", "arrival": 0, "burst": 5, "priority": 1},
        {"pid": "P1", "arrival": 2, "burst": 3, "priority": 2},
    ]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw)
    assert "Duplicate Process ID 'P1'" in str(exc.value)


def test_empty_pid():
    raw = [{"pid": "   ", "arrival": 0, "burst": 5, "priority": 1}]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw)
    assert "empty 'pid'" in str(exc.value)


def test_negative_arrival():
    raw = [{"pid": "P1", "arrival": -1, "burst": 5, "priority": 1}]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw)
    assert "arrival time must be non-negative" in str(exc.value)


def test_zero_or_negative_burst():
    raw_zero = [{"pid": "P1", "arrival": 0, "burst": 0, "priority": 1}]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw_zero)
    assert "burst time must be a strictly positive integer" in str(exc.value)

    raw_neg = [{"pid": "P1", "arrival": 0, "burst": -4, "priority": 1}]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw_neg)
    assert "burst time must be a strictly positive integer" in str(exc.value)


def test_negative_priority():
    raw = [{"pid": "P1", "arrival": 0, "burst": 5, "priority": -2}]
    with pytest.raises(ValidationError) as exc:
        validate_processes(raw)
    assert "priority must be non-negative" in str(exc.value)


def test_validate_quantum():
    assert validate_quantum(1) == 1
    assert validate_quantum("3") == 3

    with pytest.raises(ValidationError) as exc:
        validate_quantum(0)
    assert "strictly positive integer" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_quantum(-2)
    assert "strictly positive integer" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_quantum("abc")
    assert "must be an integer" in str(exc.value)


def test_validate_schedule_request():
    data = {
        "algorithm": "round_robin",
        "quantum": 2,
        "processes": [{"pid": "P1", "arrival": 0, "burst": 4, "priority": 1}],
    }
    algo, procs, q = validate_schedule_request(data)
    assert algo == "round_robin"
    assert len(procs) == 1
    assert q == 2

    # Invalid algorithm
    with pytest.raises(ValidationError) as exc:
        validate_schedule_request(
            {
                "algorithm": "unknown_algo",
                "processes": [
                    {"pid": "P1", "arrival": 0, "burst": 4, "priority": 1}
                ],
            }
        )
    assert "Invalid algorithm" in str(exc.value)
