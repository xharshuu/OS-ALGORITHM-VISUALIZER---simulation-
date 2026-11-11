"""
Priority CPU Scheduling Algorithms (Non-preemptive and Preemptive).
Convention: A smaller priority integer represents a higher priority.
"""

from typing import Any, Dict, List
from algorithms.metrics import calculate_metrics


def merge_consecutive_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge adjacent segments belonging to the same process or adjacent IDLE segments.
    """
    if not segments:
        return []

    merged: List[Dict[str, Any]] = []
    current = dict(segments[0])

    for nxt in segments[1:]:
        if (
            nxt["pid"] == current["pid"]
            and nxt["is_idle"] == current["is_idle"]
            and nxt["start"] == current["end"]
        ):
            # Extend current segment
            current["end"] = nxt["end"]
        else:
            merged.append(current)
            current = dict(nxt)

    merged.append(current)
    return merged


def schedule_priority_non_preemptive(processes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute Non-preemptive Priority CPU scheduling.

    Rules:
      - Smaller priority integer = higher priority.
      - Once CPU starts executing a process, it runs until full burst completion.
      - Ties broken by arrival time, then input order.
      - Idle CPU periods are tracked accurately.
    """
    timeline_segments: List[Dict[str, Any]] = []
    completed_pids = set()
    total_processes = len(processes)
    current_time = 0

    # Ensure processes are sorted initially by arrival, then priority, then order_index
    procs = [dict(p) for p in processes]

    while len(completed_pids) < total_processes:
        # Find all available processes that haven't completed
        ready_pool = [
            p
            for p in procs
            if p["pid"] not in completed_pids and p["arrival"] <= current_time
        ]

        if not ready_pool:
            # CPU is idle until next process arrives
            remaining_unstarted = [
                p for p in procs if p["pid"] not in completed_pids
            ]
            next_arrival = min(p["arrival"] for p in remaining_unstarted)

            if next_arrival > current_time:
                timeline_segments.append(
                    {
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arrival,
                        "is_idle": True,
                    }
                )
                current_time = next_arrival
            continue

        # Select process with highest priority (smallest number)
        # Tie-breaker: earliest arrival time, then input order
        selected = min(
            ready_pool,
            key=lambda p: (p["priority"], p["arrival"], p["order_index"]),
        )

        start_time = current_time
        end_time = start_time + selected["burst"]

        timeline_segments.append(
            {
                "pid": selected["pid"],
                "start": start_time,
                "end": end_time,
                "is_idle": False,
                "priority": selected["priority"],
            }
        )

        current_time = end_time
        completed_pids.add(selected["pid"])

    merged_segments = merge_consecutive_segments(timeline_segments)
    metrics_result = calculate_metrics(processes, merged_segments)

    return {
        "algorithm": "priority_non_preemptive",
        "algorithm_name": "Priority Scheduling (Non-preemptive)",
        "timeline": merged_segments,
        "raw_steps": timeline_segments,
        "processes": metrics_result["processes"],
        "metrics": metrics_result["summary"],
    }


def schedule_priority_preemptive(processes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute Preemptive Priority CPU scheduling.

    Rules:
      - Smaller priority integer = higher priority.
      - A newly arrived process with strictly higher priority preempts the currently running process.
      - Tied priorities do NOT preempt the currently running process.
      - Ties among ready queue are resolved by smallest priority, then earliest arrival, then input order.
      - Remaining burst time is preserved upon preemption.
      - First execution records response time.
    """
    timeline_segments: List[Dict[str, Any]] = []
    total_processes = len(processes)

    # Process state tracking
    state = {}
    for p in processes:
        state[p["pid"]] = {
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "remaining": p["burst"],
            "priority": p["priority"],
            "order_index": p["order_index"],
        }

    completed_pids = set()
    current_time = 0

    while len(completed_pids) < total_processes:
        # Check processes that have arrived and have remaining burst
        ready_pool = [
            s
            for s in state.values()
            if s["pid"] not in completed_pids and s["arrival"] <= current_time
        ]

        if not ready_pool:
            # Advance time to earliest upcoming arrival
            upcoming = [
                s for s in state.values() if s["pid"] not in completed_pids
            ]
            next_arrival = min(s["arrival"] for s in upcoming)

            if next_arrival > current_time:
                timeline_segments.append(
                    {
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arrival,
                        "is_idle": True,
                    }
                )
                current_time = next_arrival
            continue

        # Choose highest priority (smallest number)
        curr = min(
            ready_pool,
            key=lambda s: (s["priority"], s["arrival"], s["order_index"]),
        )

        finish_time = current_time + curr["remaining"]

        # Check for any future arrival that has strictly higher priority (p < curr.priority)
        # and arrives before curr finishes
        preempting_arrivals = [
            s
            for s in state.values()
            if s["pid"] not in completed_pids
            and s["arrival"] > current_time
            and s["priority"] < curr["priority"]
        ]

        if preempting_arrivals:
            earliest_preempt = min(s["arrival"] for s in preempting_arrivals)
            next_event_time = min(finish_time, earliest_preempt)
        else:
            next_event_time = finish_time

        run_duration = next_event_time - current_time

        timeline_segments.append(
            {
                "pid": curr["pid"],
                "start": current_time,
                "end": next_event_time,
                "is_idle": False,
                "priority": curr["priority"],
            }
        )

        curr["remaining"] -= run_duration
        if curr["remaining"] == 0:
            completed_pids.add(curr["pid"])

        current_time = next_event_time

    merged_segments = merge_consecutive_segments(timeline_segments)
    metrics_result = calculate_metrics(processes, merged_segments)

    return {
        "algorithm": "priority_preemptive",
        "algorithm_name": "Priority Scheduling (Preemptive)",
        "timeline": merged_segments,
        "raw_steps": timeline_segments,
        "processes": metrics_result["processes"],
        "metrics": metrics_result["summary"],
    }
