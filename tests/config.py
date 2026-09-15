"""Test configuration, client factory, and reporting utilities.

Provides centralized configuration for running integration tests against
either a live HTTP server or an in-memory ASGI application fallback.
"""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

# Add project root to sys.path so tests can import GhanaMotivationApp and main
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx

# Target server URL. Default to standard local Uvicorn port.
DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
SERVER_URL = os.getenv("TEST_SERVER_URL", DEFAULT_SERVER_URL)


class Colors:
    """ANSI color escape sequences for console output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"


def print_header(title: str) -> None:
    """Prints a styled section header banner."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")


def log_pass(test_name: str, details: str = "") -> None:
    """Logs a passing test step with green checkmark."""
    detail_str = f" - {details}" if details else ""
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {test_name}{detail_str}")


def log_fail(test_name: str, error: str) -> None:
    """Logs a failing test step with red cross."""
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {test_name}: {error}")


def log_info(msg: str) -> None:
    """Logs an informational note in yellow."""
    print(f"  {Colors.YELLOW}[INFO]{Colors.RESET} {msg}")


async def check_live_server(url: str = SERVER_URL) -> bool:
    """Checks if the FastAPI server is actively accepting HTTP connections.

    Args:
        url: The root URL to probe.

    Returns:
        True if the server responded, False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=1.5) as probe:
            response = await probe.get(f"{url}/openapi.json")
            return response.status_code == 200
    except Exception:
        return False


@asynccontextmanager
async def get_test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provides an AsyncClient configured for testing.

    Strategy:
        1. Probes `SERVER_URL` (http://127.0.0.1:8000).
        2. If reachable: uses standard HTTP network client (tests real running server).
        3. If unreachable: seamlessly falls back to `ASGITransport(app=main.app)`
           so tests still succeed even if the developer forgot to launch Uvicorn.

    Yields:
        Configured `httpx.AsyncClient` instance.
    """
    is_live = await check_live_server()

    if is_live:
        log_info(f"Connected to LIVE server at {SERVER_URL}")
        async with httpx.AsyncClient(base_url=SERVER_URL, timeout=10.0) as client:
            yield client
    else:
        log_info(f"Live server not detected at {SERVER_URL}. Using in-memory ASGI transport.")
        import main
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=10.0) as client:
            yield client
