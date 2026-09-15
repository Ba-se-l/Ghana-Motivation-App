"""Test package facade for Ghana Motivation App backend integration tests.

Exposes test runners and client utilities for modular external consumption.
"""

from .config import get_test_client, Colors, print_header, log_pass, log_fail, log_info
from .test_01_auth import test_auth_suite
from .test_02_users import test_users_suite
from .test_03_payments import test_payments_suite
from .test_04_quotes import test_quotes_suite
from .run_all_tests import run_master_test_pipeline

__all__ = (
    "get_test_client",
    "Colors",
    "print_header",
    "log_pass",
    "log_fail",
    "log_info",
    "test_auth_suite",
    "test_users_suite",
    "test_payments_suite",
    "test_quotes_suite",
    "run_master_test_pipeline",
)
