import pytest
from algorithms.round_robin import schedule_round_robin


def test_round_robin_single_process():
    procs = [{"pid": "P1", "arrival": 0, "burst": 7, "order_index": 0}]
    result = schedule_round_robin(procs, quantum=3)

    assert result["algorithm"] == "round_robin"
    # Merged timeline should be [0, 7]
    assert len(result["timeline"]) == 1
    assert result["timeline"][0]["start"] == 0
    assert result["timeline"][0]["end"] == 7

    # Raw steps should show quantum slices [0,3], [3,6], [6,7]
    assert len(result["raw_steps"]) == 3
    assert result["raw_steps"][0] == {
        "pid": "P1",
        "start": 0,
        "end": 3,
        "is_idle": False,
        "priority": 0,
    }
    assert result["raw_steps"][1] == {
        "pid": "P1",
        "start": 3,
        "end": 6,
        "is_idle": False,
        "priority": 0,
    }
    assert result["raw_steps"][2] == {
        "pid": "P1",
        "start": 6,
        "end": 7,
        "is_idle": False,
        "priority": 0,
    }

    p1 = result["processes"][0]
    assert p1["completion_time"] == 7
    assert p1["turnaround_time"] == 7
    assert p1["waiting_time"] == 0
    assert p1["response_time"] == 0


def test_round_robin_quantum_1():
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 2, "order_index": 0},
        {"pid": "P2", "arrival": 0, "burst": 3, "order_index": 1},
    ]
    result = schedule_round_robin(procs, quantum=1)

    # Raw steps: P1 (0..1), P2 (1..2), P1 (2..3), P2 (3..4), P2 (4..5)
    steps = [(s["pid"], s["start"], s["end"]) for s in result["raw_steps"]]
    assert steps == [
        ("P1", 0, 1),
        ("P2", 1, 2),
        ("P1", 2, 3),
        ("P2", 3, 4),
        ("P2", 4, 5),
    ]

    proc_map = {p["pid"]: p for p in result["processes"]}
    # P1: CT=3, TAT=3, WT=1, RT=0
    assert proc_map["P1"]["completion_time"] == 3
    assert proc_map["P1"]["turnaround_time"] == 3
    assert proc_map["P1"]["waiting_time"] == 1
    assert proc_map["P1"]["response_time"] == 0

    # P2: CT=5, TAT=5, WT=2, RT=1
    assert proc_map["P2"]["completion_time"] == 5
    assert proc_map["P2"]["turnaround_time"] == 5
    assert proc_map["P2"]["waiting_time"] == 2
    assert proc_map["P2"]["response_time"] == 1


def test_round_robin_quantum_larger_than_bursts():
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 3, "order_index": 0},
        {"pid": "P2", "arrival": 0, "burst": 4, "order_index": 1},
    ]
    result = schedule_round_robin(procs, quantum=10)

    # Acts like FCFS
    steps = [(s["pid"], s["start"], s["end"]) for s in result["raw_steps"]]
    assert steps == [("P1", 0, 3), ("P2", 3, 7)]


def test_round_robin_arrival_at_slice_boundary():
    # Crucial rule: When P1 finishes quantum at t=2, P2 arrives at t=2.
    # P2 must be queued BEFORE P1 is re-queued!
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 4, "order_index": 0},
        {"pid": "P2", "arrival": 2, "burst": 2, "order_index": 1},
    ]
    result = schedule_round_robin(procs, quantum=2)

    # Execution order:
    # 0..2: P1 (remaining 2)
    # At t=2: P2 arrives, queued first. Then P1 re-queued. Queue = [P2, P1]
    # 2..4: P2 (burst 2 finishes)
    # 4..6: P1 (remaining 2 finishes)
    steps = [(s["pid"], s["start"], s["end"]) for s in result["raw_steps"]]
    assert steps == [
        ("P1", 0, 2),
        ("P2", 2, 4),
        ("P1", 4, 6),
    ]

    proc_map = {p["pid"]: p for p in result["processes"]}
    assert proc_map["P2"]["completion_time"] == 4
    assert proc_map["P2"]["waiting_time"] == 0
    assert proc_map["P1"]["completion_time"] == 6
    assert proc_map["P1"]["waiting_time"] == 2


def test_round_robin_idle_periods():
    procs = [
        {"pid": "P1", "arrival": 2, "burst": 3, "order_index": 0},
        {"pid": "P2", "arrival": 8, "burst": 2, "order_index": 1},
    ]
    result = schedule_round_robin(procs, quantum=2)
    timeline = result["timeline"]

    # 0..2 IDLE
    # 2..5 P1
    # 5..8 IDLE
    # 8..10 P2
    assert timeline[0] == {"pid": "IDLE", "start": 0, "end": 2, "is_idle": True}
    assert timeline[1]["pid"] == "P1" and timeline[1]["start"] == 2 and timeline[1]["end"] == 5
    assert timeline[2] == {"pid": "IDLE", "start": 5, "end": 8, "is_idle": True}
    assert timeline[3]["pid"] == "P2" and timeline[3]["start"] == 8 and timeline[3]["end"] == 10


def test_round_robin_invalid_quantum():
    with pytest.raises(ValueError):
        schedule_round_robin([], quantum=0)
    with pytest.raises(ValueError):
        schedule_round_robin([], quantum=-1)
