"""
Desktop window launcher for OS Algorithm Visualizer using pywebview and Waitress.
"""

import logging
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("desktop")

DEFAULT_PORT = 5050
HOST = "127.0.0.1"


def find_available_port(start_port: int = DEFAULT_PORT, max_attempts: int = 50) -> int:
    """Find an available port on 127.0.0.1 to prevent port conflict issues."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((HOST, port))
            if result != 0:
                # Port is available
                return port
    raise RuntimeError(f"Could not find an available port on {HOST} between {start_port} and {start_port + max_attempts}.")


def run_server(host: str, port: int):
    """Run Flask application using Waitress or fallback WSGI server bound strictly to 127.0.0.1."""
    try:
        from waitress import serve
        logger.info(f"Serving via Waitress production WSGI on http://{host}:{port}")
        serve(app, host=host, port=port, threads=4, _quiet=True)
    except ImportError:
        logger.warning("Waitress not installed. Falling back to Werkzeug WSGI server on 127.0.0.1.")
        from werkzeug.serving import run_simple
        run_simple(host, port, app, threaded=True, use_debugger=False, use_reloader=False)


def wait_for_server(url: str, timeout_seconds: float = 10.0) -> bool:
    """Poll the backend health endpoint until it is ready."""
    start_time = time.time()
    health_url = f"{url.rstrip('/')}/api/health"
    logger.info(f"Waiting for backend health endpoint: {health_url}")

    while time.time() - start_time < timeout_seconds:
        try:
            with urllib.request.urlopen(health_url, timeout=1.0) as resp:
                if resp.status == 200:
                    logger.info("Backend health check passed successfully.")
                    return True
        except (urllib.error.URLError, ConnectionRefusedError, socket.timeout):
            time.sleep(0.15)
        except Exception as e:
            logger.debug(f"Health check retry: {e}")
            time.sleep(0.15)

    return False


def launch_desktop():
    """Main entrypoint for desktop application."""
    port_env = os.environ.get("PORT")
    start_port = int(port_env) if port_env and port_env.isdigit() else DEFAULT_PORT

    port = find_available_port(start_port)
    server_url = f"http://{HOST}:{port}"

    # Start backend server in a background daemon thread
    server_thread = threading.Thread(
        target=run_server,
        args=(HOST, port),
        daemon=True,
    )
    server_thread.start()

    # Wait for the backend health check
    if not wait_for_server(server_url, timeout_seconds=8.0):
        logger.error(f"Failed to start local server on {server_url}. Exiting.")
        sys.exit(1)

    # Launch desktop window
    try:
        import webview
        logger.info("Launching desktop window using pywebview...")
        window = webview.create_window(
            title="OS Algorithm Visualizer",
            url=server_url,
            width=1280,
            height=860,
            min_size=(960, 640),
            text_select=True,
        )
        webview.start(debug=False)
        logger.info("pywebview window closed. Exiting.")
    except ImportError:
        logger.warning(
            "pywebview is not installed in the current environment. "
            "Launching in native Windows standalone app window mode."
        )
        # On Windows, try launching in app mode (frameless standalone window using Edge/WebView2)
        import subprocess
        app_opened = False
        edge_paths = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        ]
        for ep in edge_paths:
            if os.path.exists(ep):
                try:
                    subprocess.Popen([ep, f"--app={server_url}", "--window-size=1280,860"])
                    app_opened = True
                    break
                except Exception as ex:
                    logger.debug(f"Edge app mode error: {ex}")

        if not app_opened:
            webbrowser.open(server_url)

        logger.info(f"OS Algorithm Visualizer running at {server_url}. Press Ctrl+C in terminal to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping desktop application...")


if __name__ == "__main__":
    launch_desktop()
