"""
Round Robin CPU Scheduling Algorithm.
"""

from collections import deque
from typing import Any, Dict, List
from algorithms.metrics import calculate_metrics
from algorithms.priority import merge_consecutive_segments


def schedule_round_robin(
    processes: List[Dict[str, Any]], quantum: int
) -> Dict[str, Any]:
    """
    Execute Round Robin CPU scheduling.

    Rules:
      - Configurable positive integer time quantum.
      - Maintains a FIFO ready queue.
      - Newly arriving processes at or before current time (including exactly at the time-slice boundary)
        are queued BEFORE an unfinished running process is re-queued.
      - Supports arbitrary arrival times, idle CPU periods, and simultaneous arrivals.
    """
    if quantum <= 0:
        raise ValueError(f"Time quantum must be a positive integer (> 0, received: {quantum})")

    timeline_segments: List[Dict[str, Any]] = []

    # Sort incoming processes by arrival time, then input order
    procs_pool = sorted(
        [
            {
                "pid": p["pid"],
                "arrival": p["arrival"],
                "burst": p["burst"],
                "remaining": p["burst"],
                "priority": p.get("priority", 0),
                "order_index": p["order_index"],
            }
            for p in processes
        ],
        key=lambda x: (x["arrival"], x["order_index"]),
    )

    ready_queue: deque = deque()
    pool_idx = 0
    total_processes = len(procs_pool)
    current_time = 0
    completed_count = 0

    def enqueue_arrivals(up_to_time: int):
        nonlocal pool_idx
        while pool_idx < total_processes and procs_pool[pool_idx]["arrival"] <= up_to_time:
            ready_queue.append(procs_pool[pool_idx])
            pool_idx += 1

    # Initial arrivals at time 0
    enqueue_arrivals(0)

    while completed_count < total_processes:
        if not ready_queue:
            # CPU is idle until next process in pool arrives
            if pool_idx < total_processes:
                next_arrival = procs_pool[pool_idx]["arrival"]
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
                enqueue_arrivals(current_time)
            continue

        curr = ready_queue.popleft()
        slice_duration = min(quantum, curr["remaining"])
        start_time = current_time
        end_time = current_time + slice_duration

        timeline_segments.append(
            {
                "pid": curr["pid"],
                "start": start_time,
                "end": end_time,
                "is_idle": False,
                "priority": curr["priority"],
            }
        )

        curr["remaining"] -= slice_duration
        current_time = end_time

        # CRITICAL ROUND ROBIN RULE:
        # Enqueue all processes arriving at or before end_time BEFORE requeuing curr
        enqueue_arrivals(current_time)

        if curr["remaining"] > 0:
            ready_queue.append(curr)
        else:
            completed_count += 1

    merged_segments = merge_consecutive_segments(timeline_segments)
    metrics_result = calculate_metrics(processes, merged_segments)

    return {
        "algorithm": "round_robin",
        "algorithm_name": f"Round Robin (Quantum = {quantum})",
        "quantum": quantum,
        "timeline": merged_segments,
        "raw_steps": timeline_segments,
        "processes": metrics_result["processes"],
        "metrics": metrics_result["summary"],
    }
