"""
Deadlock Avoidance and Safety: Banker's Algorithm.
"""

from typing import Any, Dict, List, Optional, Tuple


def calculate_need_matrix(
    max_matrix: List[List[int]], allocation_matrix: List[List[int]]
) -> List[List[int]]:
    """Compute Need[i][j] = Max[i][j] - Allocation[i][j]."""
    need = []
    for m_row, a_row in zip(max_matrix, allocation_matrix):
        need.append([m - a for m, a in zip(m_row, a_row)])
    return need


def check_safety(
    processes: List[str],
    available: List[int],
    allocation: List[List[int]],
    max_matrix: List[List[int]],
) -> Dict[str, Any]:
    """
    Run Banker's Safety Algorithm to determine if system is in a safe state
    and find a safe sequence.
    """
    n = len(processes)
    m = len(available)
    need = calculate_need_matrix(max_matrix, allocation)

    work = list(available)
    finish = [False] * n
    safe_sequence = []
    steps = []

    while len(safe_sequence) < n:
        found = False
        for i in range(n):
            if not finish[i]:
                # Check if Need[i] <= Work
                if all(need[i][j] <= work[j] for j in range(m)):
                    # Process can finish
                    prev_work = list(work)
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(processes[i])
                    found = True

                    steps.append(
                        {
                            "step": len(safe_sequence),
                            "pid": processes[i],
                            "need": need[i],
                            "prev_work": prev_work,
                            "allocated": allocation[i],
                            "new_work": list(work),
                        }
                    )
                    break

        if not found:
            # Deadlock / Unsafe state detected
            break

    is_safe = len(safe_sequence) == n
    return {
        "is_safe": is_safe,
        "safe_sequence": safe_sequence if is_safe else [],
        "need_matrix": need,
        "available": available,
        "allocation": allocation,
        "max": max_matrix,
        "processes": processes,
        "steps": steps,
        "message": (
            f"System is in a SAFE state. Safe sequence: <{' → '.join(safe_sequence)}>"
            if is_safe
            else "System is in an UNSAFE state (Deadlock may occur). No safe sequence exists."
        ),
    }


def handle_resource_request(
    processes: List[str],
    available: List[int],
    allocation: List[List[int]],
    max_matrix: List[List[int]],
    request_pid: str,
    request_vector: List[int],
) -> Dict[str, Any]:
    """
    Simulate a resource request by a specific process using Banker's Algorithm.
    """
    if request_pid not in processes:
        return {"granted": False, "error": f"Process '{request_pid}' not found."}

    p_idx = processes.index(request_pid)
    m = len(available)
    need = calculate_need_matrix(max_matrix, allocation)

    # Condition 1: Request <= Need
    if any(request_vector[j] > need[p_idx][j] for j in range(m)):
        return {
            "granted": False,
            "error": f"Process {request_pid} exceeded its declared maximum need.",
        }

    # Condition 2: Request <= Available
    if any(request_vector[j] > available[j] for j in range(m)):
        return {
            "granted": False,
            "error": f"Resources are not currently available. Process {request_pid} must wait.",
        }

    # Pretend to allocate resources
    sim_available = [available[j] - request_vector[j] for j in range(m)]
    sim_allocation = [list(row) for row in allocation]
    for j in range(m):
        sim_allocation[p_idx][j] += request_vector[j]

    # Evaluate safety
    safety_result = check_safety(processes, sim_available, sim_allocation, max_matrix)

    if safety_result["is_safe"]:
        return {
            "granted": True,
            "message": f"Request GRANTED for {request_pid}. System remains in a safe state.",
            "safe_sequence": safety_result["safe_sequence"],
            "new_available": sim_available,
            "new_allocation": sim_allocation,
        }
    else:
        return {
            "granted": False,
            "message": f"Request DENIED for {request_pid}. Granting this request leads to an UNSAFE state.",
            "error": "Granting leads to an unsafe state (Deadlock). Request must wait.",
        }
