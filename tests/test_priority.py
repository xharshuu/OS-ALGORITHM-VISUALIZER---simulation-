import pytest
from algorithms.priority import (
    schedule_priority_non_preemptive,
    schedule_priority_preemptive,
)


def test_single_process_non_preemptive():
    procs = [{"pid": "P1", "arrival": 0, "burst": 5, "priority": 1, "order_index": 0}]
    result = schedule_priority_non_preemptive(procs)

    assert result["algorithm"] == "priority_non_preemptive"
    assert len(result["timeline"]) == 1
    seg = result["timeline"][0]
    assert seg["pid"] == "P1"
    assert seg["start"] == 0
    assert seg["end"] == 5

    p1 = result["processes"][0]
    assert p1["completion_time"] == 5
    assert p1["turnaround_time"] == 5
    assert p1["waiting_time"] == 0
    assert p1["response_time"] == 0

    metrics = result["metrics"]
    assert metrics["cpu_utilization"] == 100.0
    assert metrics["total_elapsed_time"] == 5


def test_single_process_delayed_arrival():
    procs = [{"pid": "P1", "arrival": 3, "burst": 4, "priority": 1, "order_index": 0}]
    result = schedule_priority_non_preemptive(procs)

    assert len(result["timeline"]) == 2
    assert result["timeline"][0] == {
        "pid": "IDLE",
        "start": 0,
        "end": 3,
        "is_idle": True,
    }
    assert result["timeline"][1]["pid"] == "P1"
    assert result["timeline"][1]["start"] == 3
    assert result["timeline"][1]["end"] == 7

    p1 = result["processes"][0]
    assert p1["completion_time"] == 7
    assert p1["turnaround_time"] == 4
    assert p1["waiting_time"] == 0
    assert p1["response_time"] == 0


def test_multiple_processes_same_arrival_non_preemptive():
    # Smaller priority number = higher priority
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 4, "priority": 3, "order_index": 0},
        {"pid": "P2", "arrival": 0, "burst": 3, "priority": 1, "order_index": 1},
        {"pid": "P3", "arrival": 0, "burst": 2, "priority": 2, "order_index": 2},
    ]
    result = schedule_priority_non_preemptive(procs)

    # Execution order must be P2 (prio 1), P3 (prio 2), P1 (prio 3)
    pids = [s["pid"] for s in result["timeline"]]
    assert pids == ["P2", "P3", "P1"]

    proc_map = {p["pid"]: p for p in result["processes"]}
    assert proc_map["P2"]["completion_time"] == 3
    assert proc_map["P2"]["turnaround_time"] == 3
    assert proc_map["P2"]["waiting_time"] == 0

    assert proc_map["P3"]["completion_time"] == 5
    assert proc_map["P3"]["turnaround_time"] == 5
    assert proc_map["P3"]["waiting_time"] == 3

    assert proc_map["P1"]["completion_time"] == 9
    assert proc_map["P1"]["turnaround_time"] == 9
    assert proc_map["P1"]["waiting_time"] == 5

    assert result["metrics"]["average_waiting_time"] == round((0 + 3 + 5) / 3, 2)


def test_priority_preemptive_scheduling():
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 8, "priority": 3, "order_index": 0},
        {"pid": "P2", "arrival": 1, "burst": 4, "priority": 1, "order_index": 1},
        {"pid": "P3", "arrival": 2, "burst": 2, "priority": 2, "order_index": 2},
    ]
    result = schedule_priority_preemptive(procs)

    # Timeline:
    # 0..1: P1 (burst remaining 7)
    # 1..5: P2 (runs to completion, ignores P3 arriving at 2 because P2 prio 1 < P3 prio 2)
    # 5..7: P3 (prio 2 < P1 prio 3)
    # 7..14: P1 (remaining 7)
    timeline = result["timeline"]
    assert len(timeline) == 4
    assert timeline[0]["pid"] == "P1" and timeline[0]["start"] == 0 and timeline[0]["end"] == 1
    assert timeline[1]["pid"] == "P2" and timeline[1]["start"] == 1 and timeline[1]["end"] == 5
    assert timeline[2]["pid"] == "P3" and timeline[2]["start"] == 5 and timeline[2]["end"] == 7
    assert timeline[3]["pid"] == "P1" and timeline[3]["start"] == 7 and timeline[3]["end"] == 14

    proc_map = {p["pid"]: p for p in result["processes"]}
    # P1: CT=14, TAT=14, WT=6, RT=0
    assert proc_map["P1"]["completion_time"] == 14
    assert proc_map["P1"]["turnaround_time"] == 14
    assert proc_map["P1"]["waiting_time"] == 6
    assert proc_map["P1"]["response_time"] == 0

    # P2: CT=5, TAT=4, WT=0, RT=0
    assert proc_map["P2"]["completion_time"] == 5
    assert proc_map["P2"]["turnaround_time"] == 4
    assert proc_map["P2"]["waiting_time"] == 0
    assert proc_map["P2"]["response_time"] == 0

    # P3: CT=7, TAT=5, WT=3, RT=3
    assert proc_map["P3"]["completion_time"] == 7
    assert proc_map["P3"]["turnaround_time"] == 5
    assert proc_map["P3"]["waiting_time"] == 3
    assert proc_map["P3"]["response_time"] == 3

    assert result["metrics"]["total_burst_time"] == 14
    assert result["metrics"]["total_elapsed_time"] == 14
    assert result["metrics"]["cpu_utilization"] == 100.0


def test_equal_priorities_tie_break():
    # Both priority 1, arrival 0 vs arrival 1
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 3, "priority": 1, "order_index": 0},
        {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1, "order_index": 1},
    ]
    # In preemptive priority, arriving equal priority does NOT preempt running process
    result = schedule_priority_preemptive(procs)
    pids = [s["pid"] for s in result["timeline"]]
    assert pids == ["P1", "P2"]
    assert result["timeline"][0]["end"] == 3
    assert result["timeline"][1]["end"] == 6


def test_idle_periods_between_processes():
    procs = [
        {"pid": "P1", "arrival": 1, "burst": 2, "priority": 2, "order_index": 0},
        {"pid": "P2", "arrival": 6, "burst": 3, "priority": 1, "order_index": 1},
    ]
    result = schedule_priority_preemptive(procs)
    timeline = result["timeline"]

    # 0..1 IDLE
    # 1..3 P1
    # 3..6 IDLE
    # 6..9 P2
    assert len(timeline) == 4
    assert timeline[0]["is_idle"] is True and timeline[0]["end"] == 1
    assert timeline[1]["pid"] == "P1" and timeline[1]["end"] == 3
    assert timeline[2]["is_idle"] is True and timeline[2]["start"] == 3 and timeline[2]["end"] == 6
    assert timeline[3]["pid"] == "P2" and timeline[3]["start"] == 6 and timeline[3]["end"] == 9

    assert result["metrics"]["total_elapsed_time"] == 9
    assert result["metrics"]["total_burst_time"] == 5
    assert result["metrics"]["cpu_utilization"] == round((5 / 9) * 100, 2)
