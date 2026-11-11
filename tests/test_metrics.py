from algorithms.metrics import calculate_metrics
from algorithms.priority import schedule_priority_non_preemptive, schedule_priority_preemptive
from algorithms.round_robin import schedule_round_robin


def test_metrics_definitions_and_formulas():
    processes = [
        {"pid": "P1", "arrival": 0, "burst": 4, "priority": 1, "order_index": 0},
        {"pid": "P2", "arrival": 1, "burst": 3, "priority": 2, "order_index": 1},
    ]
    # Synthetic timeline segments
    timeline = [
        {"pid": "P1", "start": 0, "end": 4, "is_idle": False},
        {"pid": "P2", "start": 4, "end": 7, "is_idle": False},
    ]

    result = calculate_metrics(processes, timeline)
    p_map = {p["pid"]: p for p in result["processes"]}

    for pid, p in p_map.items():
        assert p["turnaround_time"] == p["completion_time"] - p["arrival"]
        assert p["waiting_time"] == p["turnaround_time"] - p["burst"]
        assert p["response_time"] == p["first_start"] - p["arrival"]

    summary = result["summary"]
    assert summary["total_burst_time"] == 7
    assert summary["total_elapsed_time"] == 7
    assert summary["cpu_utilization"] == 100.0
    assert summary["throughput"] == round(2 / 7, 4)


def test_metrics_with_idle_periods():
    processes = [
        {"pid": "P1", "arrival": 2, "burst": 3, "priority": 1, "order_index": 0},
    ]
    timeline = [
        {"pid": "IDLE", "start": 0, "end": 2, "is_idle": True},
        {"pid": "P1", "start": 2, "end": 5, "is_idle": False},
    ]
    result = calculate_metrics(processes, timeline)
    summary = result["summary"]

    assert summary["total_burst_time"] == 3
    assert summary["total_elapsed_time"] == 5
    assert summary["cpu_utilization"] == round((3 / 5) * 100, 2)
    assert summary["throughput"] == round(1 / 5, 4)


def test_timeline_non_overlapping_and_burst_conservation():
    procs = [
        {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2, "order_index": 0},
        {"pid": "P2", "arrival": 2, "burst": 3, "priority": 1, "order_index": 1},
        {"pid": "P3", "arrival": 4, "burst": 4, "priority": 3, "order_index": 2},
    ]

    for run_func in [
        lambda: schedule_priority_non_preemptive(procs),
        lambda: schedule_priority_preemptive(procs),
        lambda: schedule_round_robin(procs, quantum=2),
    ]:
        res = run_func()
        timeline = res["timeline"]

        # 1. Non-overlapping segments: seg[i].end == seg[i+1].start
        for i in range(len(timeline) - 1):
            assert timeline[i]["end"] == timeline[i + 1]["start"], (
                f"Overlap or gap detected between {timeline[i]} and {timeline[i+1]}"
            )

        # 2. Total executed non-idle burst must equal sum of input bursts
        total_executed_burst = sum(
            s["end"] - s["start"] for s in timeline if not s.get("is_idle") and s["pid"] != "IDLE"
        )
        assert total_executed_burst == 12  # 5 + 3 + 4


def test_zero_duration_elapsed_safely():
    result = calculate_metrics([], [])
    assert result["summary"]["total_elapsed_time"] == 0
    assert result["summary"]["cpu_utilization"] == 0.0
    assert result["summary"]["throughput"] == 0.0
