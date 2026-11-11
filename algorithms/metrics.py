"""
Performance metrics calculations for CPU scheduling algorithms.
"""

from typing import Any, Dict, List


def calculate_metrics(
    processes: List[Dict[str, Any]],
    timeline_segments: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculate per-process and aggregate scheduling performance metrics.

    Metrics definitions:
      - Completion Time (CT): Time when process finishes execution.
      - Turnaround Time (TAT): CT - AT
      - Waiting Time (WT): TAT - BT
      - Response Time (RT): First Start Time - AT

    Aggregate metrics:
      - Average WT
      - Average TAT
      - Average RT
      - Total Elapsed Time: Final completion time (interval from time zero to final CT)
      - CPU Utilization (%): (Total Burst Time / Total Elapsed Time) * 100
      - Throughput: Completed Processes / Total Elapsed Time
    """
    process_results: List[Dict[str, Any]] = []

    # Map first start times and completion times
    first_starts: Dict[str, int] = {}
    last_ends: Dict[str, int] = {}

    for seg in timeline_segments:
        pid = seg.get("pid")
        if seg.get("is_idle") or pid == "IDLE":
            continue
        start = seg["start"]
        end = seg["end"]
        if pid not in first_starts:
            first_starts[pid] = start
        last_ends[pid] = max(last_ends.get(pid, end), end)

    total_wt = 0.0
    total_tat = 0.0
    total_rt = 0.0
    total_burst = 0

    for p in processes:
        pid = p["pid"]
        arrival = p["arrival"]
        burst = p["burst"]
        priority = p.get("priority", 0)

        # First start time
        first_start = first_starts.get(pid, arrival)
        # Completion time
        ct = last_ends.get(pid, arrival + burst)

        tat = ct - arrival
        wt = tat - burst
        rt = first_start - arrival

        total_wt += wt
        total_tat += tat
        total_rt += rt
        total_burst += burst

        process_results.append(
            {
                "pid": pid,
                "arrival": arrival,
                "burst": burst,
                "priority": priority,
                "first_start": first_start,
                "completion_time": ct,
                "turnaround_time": tat,
                "waiting_time": wt,
                "response_time": rt,
            }
        )

    # Sort results by input order or PID
    num_processes = len(processes)

    # Calculate final completion time
    final_ct = 0
    if timeline_segments:
        final_ct = max(seg["end"] for seg in timeline_segments)
    elif process_results:
        final_ct = max(p["completion_time"] for p in process_results)

    total_elapsed_time = final_ct  # Interval from time zero to final completion time

    avg_wt = round(total_wt / num_processes, 2) if num_processes > 0 else 0.0
    avg_tat = round(total_tat / num_processes, 2) if num_processes > 0 else 0.0
    avg_rt = round(total_rt / num_processes, 2) if num_processes > 0 else 0.0

    if total_elapsed_time > 0:
        cpu_utilization = round((total_burst / total_elapsed_time) * 100.0, 2)
        throughput = round(num_processes / total_elapsed_time, 4)
    else:
        cpu_utilization = 0.0
        throughput = 0.0

    return {
        "processes": process_results,
        "summary": {
            "num_processes": num_processes,
            "total_burst_time": total_burst,
            "total_elapsed_time": total_elapsed_time,
            "average_waiting_time": avg_wt,
            "average_turnaround_time": avg_tat,
            "average_response_time": avg_rt,
            "cpu_utilization": cpu_utilization,
            "throughput": throughput,
        },
    }
