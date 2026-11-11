import threading
import time
from desktop import find_available_port, wait_for_server, run_server, HOST


def test_find_available_port():
    port = find_available_port(5100)
    assert isinstance(port, int)
    assert 5100 <= port < 5150


def test_server_startup_and_health_check():
    port = find_available_port(5200)
    server_thread = threading.Thread(
        target=run_server,
        args=(HOST, port),
        daemon=True,
    )
    server_thread.start()

    url = f"http://{HOST}:{port}"
    healthy = wait_for_server(url, timeout_seconds=5.0)
    assert healthy is True
