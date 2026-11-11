"""
Flask application and JSON API for OS Algorithm Visualizer.
Supports CPU Scheduling, Contiguous Memory Allocation, Page Replacement,
Deadlock (Banker's Algorithm), and Process State Machine.
"""

import logging
from typing import Any, Dict
from flask import Flask, jsonify, render_template, request

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
from algorithms.deadlock import check_safety, handle_resource_request
from algorithms.process_states import ProcessStateMachine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Global state machine instance for Process States demo
state_machine = ProcessStateMachine()
# Initialize with 3 default processes in different states
state_machine.create_process("P1", priority=1, memory_mb=128)
state_machine.transition("P1", "admit")
state_machine.transition("P1", "dispatch")

state_machine.create_process("P2", priority=2, memory_mb=256)
state_machine.transition("P2", "admit")

state_machine.create_process("P3", priority=3, memory_mb=64)


@app.route("/")
def index():
    """Render the main single-page application dashboard."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint for desktop launcher and monitoring."""
    return jsonify({"status": "ok", "app": "OS Algorithm Visualizer", "version": "2.0.0"}), 200


# ==========================================
# 1. CPU Scheduling Routes
# ==========================================

@app.route("/api/schedule", methods=["POST"])
def schedule_simulation():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON in request body."}), 400

        algorithm, processes, quantum = validate_schedule_request(data)

        if algorithm == "priority_non_preemptive":
            result = schedule_priority_non_preemptive(processes)
        elif algorithm == "priority_preemptive":
            result = schedule_priority_preemptive(processes)
        elif algorithm == "round_robin":
            result = schedule_round_robin(processes, quantum=quantum)
        else:
            return jsonify({"error": f"Unsupported algorithm '{algorithm}'"}), 400

        result["normalized_input"] = {
            "algorithm": algorithm,
            "quantum": quantum if algorithm == "round_robin" else None,
            "processes_count": len(processes),
        }
        return jsonify(result), 200

    except ValidationError as ve:
        logger.warning(f"Validation error in /api/schedule: {ve.message}")
        return jsonify(ve.to_dict()), 400
    except Exception as exc:
        logger.error(f"Unexpected error in /api/schedule: {str(exc)}", exc_info=True)
        return (
            jsonify({"error": "An internal error occurred during simulation. Please check process inputs."}),
            500,
        )


@app.route("/api/compare", methods=["POST"])
def compare_algorithms():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON in request body."}), 400

        raw_processes = data.get("processes")
        processes = validate_processes(raw_processes)

        quantum_val = data.get("quantum", 2)
        quantum = validate_quantum(quantum_val)

        res_p_non = schedule_priority_non_preemptive(processes)
        res_p_pre = schedule_priority_preemptive(processes)
        res_rr = schedule_round_robin(processes, quantum=quantum)

        comparison = {
            "dataset_size": len(processes),
            "quantum": quantum,
            "algorithms": {
                "priority_non_preemptive": {
                    "name": "Priority (Non-preemptive)",
                    "metrics": res_p_non["metrics"],
                    "processes": res_p_non["processes"],
                },
                "priority_preemptive": {
                    "name": "Priority (Preemptive)",
                    "metrics": res_p_pre["metrics"],
                    "processes": res_p_pre["processes"],
                },
                "round_robin": {
                    "name": f"Round Robin (Q={quantum})",
                    "metrics": res_rr["metrics"],
                    "processes": res_rr["processes"],
                },
            },
        }

        return jsonify(comparison), 200

    except ValidationError as ve:
        logger.warning(f"Validation error in /api/compare: {ve.message}")
        return jsonify(ve.to_dict()), 400
    except Exception as exc:
        logger.error(f"Unexpected error in /api/compare: {str(exc)}", exc_info=True)
        return (
            jsonify({"error": "An internal error occurred during comparison."}),
            500,
        )


# ==========================================
# 2. Memory Allocation Routes
# ==========================================

@app.route("/api/memory/allocate", methods=["POST"])
def api_allocate_memory():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    data = request.get_json(silent=True) or {}
    blocks = data.get("blocks", [])
    processes = data.get("processes", [])
    algorithm = data.get("algorithm", "first_fit")

    if not blocks:
        return jsonify({"error": "At least one memory block is required."}), 400
    if not processes:
        return jsonify({"error": "At least one process memory request is required."}), 400

    try:
        result = allocate_memory(blocks, processes, algorithm=algorithm)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"Error in memory allocation: {exc}")
        return jsonify({"error": str(exc)}), 400


# ==========================================
# 3. Page Replacement Routes
# ==========================================

@app.route("/api/page-replacement", methods=["POST"])
def api_page_replacement():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    data = request.get_json(silent=True) or {}
    ref_string = data.get("reference_string", [])
    num_frames = int(data.get("num_frames", 3))
    algorithm = data.get("algorithm", "fifo")

    try:
        if algorithm == "compare":
            result = compare_page_replacements(ref_string, num_frames)
        else:
            result = simulate_page_replacement(ref_string, num_frames, algorithm)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"Error in page replacement: {exc}")
        return jsonify({"error": str(exc)}), 400


# ==========================================
# 4. Deadlock (Banker's Algorithm) Routes
# ==========================================

@app.route("/api/deadlock/safety", methods=["POST"])
def api_deadlock_safety():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    data = request.get_json(silent=True) or {}
    processes = data.get("processes", [])
    available = data.get("available", [])
    allocation = data.get("allocation", [])
    max_matrix = data.get("max", [])

    if not processes or not available or not allocation or not max_matrix:
        return jsonify({"error": "Processes, available vector, allocation matrix, and max matrix are required."}), 400

    try:
        result = check_safety(processes, available, allocation, max_matrix)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"Error in deadlock safety check: {exc}")
        return jsonify({"error": str(exc)}), 400


@app.route("/api/deadlock/request", methods=["POST"])
def api_deadlock_request():
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json."}), 400

    data = request.get_json(silent=True) or {}
    processes = data.get("processes", [])
    available = data.get("available", [])
    allocation = data.get("allocation", [])
    max_matrix = data.get("max", [])
    request_pid = data.get("request_pid")
    request_vector = data.get("request_vector", [])

    try:
        result = handle_resource_request(
            processes, available, allocation, max_matrix, request_pid, request_vector
        )
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"Error in deadlock resource request: {exc}")
        return jsonify({"error": str(exc)}), 400


# ==========================================
# 5. Process States Routes
# ==========================================

@app.route("/api/process-states/snapshot", methods=["GET"])
def api_process_states_snapshot():
    return jsonify(state_machine.get_system_snapshot()), 200


@app.route("/api/process-states/create", methods=["POST"])
def api_process_states_create():
    data = request.get_json(silent=True) or {}
    pid = data.get("pid")
    priority = int(data.get("priority", 1))
    memory_mb = int(data.get("memory_mb", 128))

    pcb = state_machine.create_process(pid=pid, priority=priority, memory_mb=memory_mb)
    return jsonify({"pcb": pcb, "snapshot": state_machine.get_system_snapshot()}), 200


@app.route("/api/process-states/transition", methods=["POST"])
def api_process_states_transition():
    data = request.get_json(silent=True) or {}
    pid = data.get("pid")
    action = data.get("action")

    if not pid or not action:
        return jsonify({"error": "pid and action are required."}), 400

    try:
        pcb = state_machine.transition(pid, action)
        return jsonify({"pcb": pcb, "snapshot": state_machine.get_system_snapshot()}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/process-states/reset", methods=["POST"])
def api_process_states_reset():
    global state_machine
    state_machine = ProcessStateMachine()
    state_machine.create_process("P1", priority=1, memory_mb=128)
    state_machine.transition("P1", "admit")
    state_machine.transition("P1", "dispatch")

    state_machine.create_process("P2", priority=2, memory_mb=256)
    state_machine.transition("P2", "admit")

    state_machine.create_process("P3", priority=3, memory_mb=64)
    return jsonify(state_machine.get_system_snapshot()), 200


# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API route not found."}), 404
    return render_template("index.html"), 404


@app.errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method not allowed."}), 405


@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
