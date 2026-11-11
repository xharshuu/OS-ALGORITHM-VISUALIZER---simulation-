"""
Scheduling, Memory, Page Replacement, Deadlock, and Process State Algorithms Module.
"""

from algorithms.metrics import calculate_metrics
from algorithms.priority import (
    schedule_priority_non_preemptive,
    schedule_priority_preemptive,
)
from algorithms.round_robin import schedule_round_robin
from algorithms.validation import (
    ValidationError,
    validate_processes,
    validate_quantum,
    validate_schedule_request,
)
from algorithms.memory import allocate_memory
from algorithms.page_replacement import simulate_page_replacement, compare_page_replacements
from algorithms.deadlock import check_safety, handle_resource_request, calculate_need_matrix
from algorithms.process_states import ProcessStateMachine

__all__ = [
    "ValidationError",
    "validate_processes",
    "validate_quantum",
    "validate_schedule_request",
    "calculate_metrics",
    "schedule_priority_non_preemptive",
    "schedule_priority_preemptive",
    "schedule_round_robin",
    "allocate_memory",
    "simulate_page_replacement",
    "compare_page_replacements",
    "check_safety",
    "handle_resource_request",
    "calculate_need_matrix",
    "ProcessStateMachine",
]
