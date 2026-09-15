"""Master integration test orchestrator for Ghana Motivation App backend.

Sequentially executes all domain test suites against the running FastAPI
instance (or in-memory ASGI fallback), benchmarks execution durations,
and prints an executive summary report card.

Execution:
    python tests/run_all_tests.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.config import Colors, print_header
from tests.test_01_auth import test_auth_suite
from tests.test_02_users import test_users_suite
from tests.test_03_payments import test_payments_suite
from tests.test_04_quotes import test_quotes_suite


async def run_master_test_pipeline() -> bool:
    """Orchestrates sequential execution of all domain test suites.

    Returns:
        True if all test suites passed without error, False otherwise.
    """
    suites = [
        ("Authentication & Sessions (/api/v1/auth)", test_auth_suite),
        ("User Profile & Security (/api/v1/users)", test_users_suite),
        ("Payments & Webhooks (/api/v1/payments)", test_payments_suite),
        ("Quotes & Offline Caching (/api/v1/quotes)", test_quotes_suite),
    ]

    results: list[tuple[str, bool, float]] = []
    pipeline_start = time.perf_counter()

    print_header("GHANA MOTIVATION BACKEND - ENTERPRISE TEST RUNNER")
    print(f"{Colors.YELLOW}Starting full test pipeline across {len(suites)} domains...{Colors.RESET}\n")

    for suite_name, suite_func in suites:
        start_time = time.perf_counter()
        try:
            passed = await suite_func()
        except Exception as exc:
            print(f"\n{Colors.RED}[CRITICAL EXCEPTION IN {suite_name}]: {exc}{Colors.RESET}")
            passed = False
        duration = time.perf_counter() - start_time
        results.append((suite_name, passed, duration))

    pipeline_duration = time.perf_counter() - pipeline_start

    # Print Executive Summary Dashboard
    print(f"\n{Colors.BOLD}{'=' * 78}{Colors.RESET}")
    print(f"{Colors.BOLD}{'SUMMARY TEST EXECUTION REPORT':^78}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 78}{Colors.RESET}")
    print(f"{'Domain Suite':<48} | {'Status':<10} | {'Duration':>12}")
    print(f"{'-' * 48}-+-{'-' * 10}-+-{'-' * 12}")

    all_passed = True
    for name, passed, dur in results:
        status_str = f"{Colors.GREEN}PASSED{Colors.RESET}" if passed else f"{Colors.RED}FAILED{Colors.RESET}"
        if not passed:
            all_passed = False
        print(f"{name:<48} | {status_str:<19} | {dur:>10.2f}s")

    print(f"{'-' * 78}")
    total_passed = sum(1 for _, p, _ in results if p)
    total_failed = len(results) - total_passed

    summary_color = Colors.GREEN if all_passed else Colors.RED
    print(
        f"Total Suites: {len(results)} | "
        f"{Colors.GREEN}Passed: {total_passed}{Colors.RESET} | "
        f"{Colors.RED if total_failed > 0 else Colors.GREEN}Failed: {total_failed}{Colors.RESET} | "
        f"Total Time: {pipeline_duration:.2f}s"
    )
    print(f"{Colors.BOLD}{'=' * 78}{Colors.RESET}")

    if all_passed:
        print(f"\n{summary_color}{Colors.BOLD}[VERDICT] ALL TESTS PASSED PERFECTLY. SYSTEM READY FOR PRODUCTION.{Colors.RESET}\n")
    else:
        print(f"\n{summary_color}{Colors.BOLD}[VERDICT] SOME TESTS FAILED. CHECK LOGS ABOVE FOR DETAILS.{Colors.RESET}\n")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_master_test_pipeline())
    sys.exit(0 if success else 1)
