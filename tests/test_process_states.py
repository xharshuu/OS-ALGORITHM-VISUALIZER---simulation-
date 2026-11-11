import pytest
from algorithms.process_states import ProcessStateMachine


def test_process_lifecycle_transitions():
    sm = ProcessStateMachine()
    p1 = sm.create_process("P1", priority=1)
    assert p1["state"] == "NEW"

    # NEW -> READY
    sm.transition("P1", "admit")
    assert sm.processes["P1"]["state"] == "READY"

    # READY -> RUNNING
    sm.transition("P1", "dispatch")
    assert sm.processes["P1"]["state"] == "RUNNING"

    # RUNNING -> WAITING (I/O)
    sm.transition("P1", "io_request")
    assert sm.processes["P1"]["state"] == "WAITING"

    # WAITING -> READY (I/O complete)
    sm.transition("P1", "io_complete")
    assert sm.processes["P1"]["state"] == "READY"

    # READY -> RUNNING
    sm.transition("P1", "dispatch")
    assert sm.processes["P1"]["state"] == "RUNNING"

    # RUNNING -> TERMINATED
    sm.transition("P1", "exit")
    assert sm.processes["P1"]["state"] == "TERMINATED"


def test_invalid_state_transition():
    sm = ProcessStateMachine()
    sm.create_process("P1")
    # Cannot dispatch directly from NEW (must be admitted first)
    with pytest.raises(ValueError):
        sm.transition("P1", "dispatch")
