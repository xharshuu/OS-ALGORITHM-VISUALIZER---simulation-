"""
Process State Transition & Process Control Block (PCB) Simulator.
"""

from typing import Any, Dict, List, Optional


class ProcessStateMachine:
    """Simulates 5-state process lifecycle (New, Ready, Running, Waiting, Terminated)."""

    def __init__(self):
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.next_pid = 1

    def create_process(
        self, pid: Optional[str] = None, priority: int = 1, memory_mb: int = 128
    ) -> Dict[str, Any]:
        """Create a new process in NEW state."""
        if not pid:
            pid = f"P{self.next_pid}"
            self.next_pid += 1

        pcb = {
            "pid": pid,
            "state": "NEW",
            "priority": priority,
            "program_counter": 0,
            "cpu_time_used": 0,
            "memory_mb": memory_mb,
            "io_cycles": 0,
            "history": ["Created in NEW state"],
        }
        self.processes[pid] = pcb
        return pcb

    def transition(self, pid: str, action: str) -> Dict[str, Any]:
        """
        Transition process state based on OS event action:
          - admit: NEW -> READY
          - dispatch: READY -> RUNNING
          - timeout: RUNNING -> READY
          - io_request: RUNNING -> WAITING
          - io_complete: WAITING -> READY
          - exit: RUNNING -> TERMINATED
        """
        if pid not in self.processes:
            raise ValueError(f"Process '{pid}' not found.")

        pcb = self.processes[pid]
        curr_state = pcb["state"]

        if action == "admit":
            if curr_state != "NEW":
                raise ValueError(f"Cannot admit process from state '{curr_state}' (must be NEW).")
            pcb["state"] = "READY"
            pcb["history"].append("Admitted to READY queue")

        elif action == "dispatch":
            if curr_state != "READY":
                raise ValueError(f"Cannot dispatch process from state '{curr_state}' (must be READY).")
            # If any other process is RUNNING, it must first be preempted or yield
            for other_pid, other_pcb in self.processes.items():
                if other_pcb["state"] == "RUNNING" and other_pid != pid:
                    other_pcb["state"] = "READY"
                    other_pcb["history"].append("Preempted to READY by CPU dispatcher")

            pcb["state"] = "RUNNING"
            pcb["program_counter"] += 10
            pcb["cpu_time_used"] += 1
            pcb["history"].append("Dispatched to RUNNING state")

        elif action == "timeout":
            if curr_state != "RUNNING":
                raise ValueError(f"Cannot timeout process in state '{curr_state}' (must be RUNNING).")
            pcb["state"] = "READY"
            pcb["history"].append("Time slice expired -> returned to READY")

        elif action == "io_request":
            if curr_state != "RUNNING":
                raise ValueError(f"Cannot request I/O from state '{curr_state}' (must be RUNNING).")
            pcb["state"] = "WAITING"
            pcb["io_cycles"] += 1
            pcb["history"].append("I/O request initiated -> WAITING")

        elif action == "io_complete":
            if curr_state != "WAITING":
                raise ValueError(f"Cannot complete I/O from state '{curr_state}' (must be WAITING).")
            pcb["state"] = "READY"
            pcb["history"].append("I/O completed -> returned to READY")

        elif action == "exit":
            if curr_state != "RUNNING":
                raise ValueError(f"Cannot terminate process from state '{curr_state}' (must be RUNNING).")
            pcb["state"] = "TERMINATED"
            pcb["history"].append("Process terminated successfully")
        else:
            raise ValueError(f"Unknown state transition action: '{action}'")

        return pcb

    def get_system_snapshot(self) -> Dict[str, Any]:
        """Categorize all processes into their respective state queues."""
        queues = {
            "NEW": [],
            "READY": [],
            "RUNNING": [],
            "WAITING": [],
            "TERMINATED": [],
        }
        for pid, pcb in self.processes.items():
            state = pcb["state"]
            if state in queues:
                queues[state].append(pcb)

        return {
            "total_processes": len(self.processes),
            "queues": queues,
            "all_pcbs": list(self.processes.values()),
        }
