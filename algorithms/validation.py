"""
Input validation for CPU scheduling algorithms.
"""

from typing import Any, Dict, List, Tuple


class ValidationError(Exception):
    """Custom exception raised when process or algorithm parameters fail validation."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.message = message
        self.field = field

    def to_dict(self) -> Dict[str, Any]:
        result = {"error": self.message}
        if self.field:
            result["field"] = self.field
        return result


def validate_processes(processes_raw: Any) -> List[Dict[str, Any]]:
    """
    Validate a list of process dictionaries.

    Each process must contain:
      - pid: non-empty string, unique across the set
      - arrival: non-negative integer (>= 0)
      - burst: positive integer (> 0)
      - priority: non-negative integer (>= 0)

    Returns:
      Normalized list of process dictionaries.
    """
    if not isinstance(processes_raw, list):
        raise ValidationError("Processes must be provided as a list.", "processes")

    if len(processes_raw) == 0:
        raise ValidationError("At least one process is required.", "processes")

    normalized: List[Dict[str, Any]] = []
    seen_pids = set()

    for idx, item in enumerate(processes_raw):
        if not isinstance(item, dict):
            raise ValidationError(
                f"Process at index {idx} must be a valid object/dictionary.",
                f"processes[{idx}]",
            )

        # Validate PID
        pid_val = item.get("pid")
        if pid_val is None:
            raise ValidationError(
                f"Process at index {idx} is missing 'pid'.",
                f"processes[{idx}].pid",
            )
        pid = str(pid_val).strip()
        if not pid:
            raise ValidationError(
                f"Process at index {idx} has an empty 'pid'.",
                f"processes[{idx}].pid",
            )
        if pid in seen_pids:
            raise ValidationError(
                f"Duplicate Process ID '{pid}' detected. Process IDs must be unique.",
                f"processes[{idx}].pid",
            )
        seen_pids.add(pid)

        # Validate Arrival Time
        arrival_val = item.get("arrival")
        if arrival_val is None:
            raise ValidationError(
                f"Process '{pid}' is missing 'arrival' time.",
                f"processes[{idx}].arrival",
            )
        try:
            arrival = int(arrival_val)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Process '{pid}' arrival time must be an integer (received: {arrival_val}).",
                f"processes[{idx}].arrival",
            )
        if arrival < 0:
            raise ValidationError(
                f"Process '{pid}' arrival time must be non-negative (received: {arrival}).",
                f"processes[{idx}].arrival",
            )

        # Validate Burst Time
        burst_val = item.get("burst")
        if burst_val is None:
            raise ValidationError(
                f"Process '{pid}' is missing 'burst' time.",
                f"processes[{idx}].burst",
            )
        try:
            burst = int(burst_val)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Process '{pid}' burst time must be an integer (received: {burst_val}).",
                f"processes[{idx}].burst",
            )
        if burst <= 0:
            raise ValidationError(
                f"Process '{pid}' burst time must be a strictly positive integer (> 0, received: {burst}).",
                f"processes[{idx}].burst",
            )

        # Validate Priority
        priority_val = item.get("priority", 0)
        try:
            priority = int(priority_val)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Process '{pid}' priority must be an integer (received: {priority_val}).",
                f"processes[{idx}].priority",
            )
        if priority < 0:
            raise ValidationError(
                f"Process '{pid}' priority must be non-negative (received: {priority}).",
                f"processes[{idx}].priority",
            )

        normalized.append(
            {
                "pid": pid,
                "arrival": arrival,
                "burst": burst,
                "priority": priority,
                "order_index": idx,
            }
        )

    return normalized


def validate_quantum(quantum_raw: Any) -> int:
    """
    Validate Round Robin time quantum. Must be a positive integer (>= 1).
    """
    if quantum_raw is None:
        raise ValidationError(
            "Time quantum is required for Round Robin scheduling.", "quantum"
        )
    try:
        quantum = int(quantum_raw)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Time quantum must be an integer (received: {quantum_raw}).", "quantum"
        )
    if quantum <= 0:
        raise ValidationError(
            f"Time quantum must be a strictly positive integer (> 0, received: {quantum}).",
            "quantum",
        )
    return quantum


def validate_schedule_request(
    data: Any,
) -> Tuple[str, List[Dict[str, Any]], int]:
    """
    Validate full scheduling API payload.

    Expected payload:
      {
        "algorithm": "priority_non_preemptive" | "priority_preemptive" | "round_robin",
        "processes": [...],
        "quantum": int (only required if algorithm is round_robin)
      }
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    algorithm = data.get("algorithm")
    valid_algorithms = [
        "priority_non_preemptive",
        "priority_preemptive",
        "round_robin",
    ]
    if not algorithm or algorithm not in valid_algorithms:
        raise ValidationError(
            f"Invalid algorithm '{algorithm}'. Supported algorithms: {', '.join(valid_algorithms)}.",
            "algorithm",
        )

    processes = validate_processes(data.get("processes"))

    quantum = 1
    if algorithm == "round_robin":
        quantum = validate_quantum(data.get("quantum"))

    return algorithm, processes, quantum
