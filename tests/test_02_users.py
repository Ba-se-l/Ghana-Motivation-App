"""User endpoint test suite.

Validates all routes under `/api/v1/users`:
- Profile retrieval (/users/me - authorized and unauthorized)
- User status calculation (/users/status - trial state, premium flag)
- Password change (/users/me/password - credential verification and rotation)
"""

import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.config import get_test_client, print_header, log_pass, log_fail


async def test_users_suite() -> bool:
    """Runs all user profile tests sequentially.

    Returns:
        True if all tests in the suite passed, False otherwise.
    """
    print_header("TEST SUITE 2: USER PROFILE & STATUS (/api/v1/users)")
    all_passed = True

    async with get_test_client() as client:
        ts = int(time.time())
        email = f"usertest_{ts}@example.com"
        password = "InitialPassword123!"

        # -------------------------------------------------------------
        # Setup: Register and Login a fresh user
        # -------------------------------------------------------------
        await client.post("/api/v1/auth/register", json={
            "name": "User Tester",
            "email": email,
            "password": password,
            "device_fingerprint": f"DEV_{ts}",
        })
        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password,
        })
        tokens = login_res.json()
        access_token = tokens["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # -------------------------------------------------------------
        # 1. GET /users/me Unauthorized (401)
        # -------------------------------------------------------------
        res = await client.get("/api/v1/users/me")
        if res.status_code == 401:
            log_pass("GET /users/me (No Auth) - 401 Unauthorized")
        else:
            log_fail("GET /users/me (No Auth)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 2. GET /users/me Authorized (200 OK)
        # -------------------------------------------------------------
        res = await client.get("/api/v1/users/me", headers=auth_headers)
        data = res.json()
        if res.status_code == 200 and data.get("email") == email:
            log_pass("GET /users/me (Authorized) - 200 OK", f"Name: {data.get('name')}")
        else:
            log_fail("GET /users/me (Authorized)", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 3. GET /users/status Unauthorized (401)
        # -------------------------------------------------------------
        res = await client.get("/api/v1/users/status")
        if res.status_code == 401:
            log_pass("GET /users/status (No Auth) - 401 Unauthorized")
        else:
            log_fail("GET /users/status (No Auth)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 4. GET /users/status Authorized (200 OK)
        # -------------------------------------------------------------
        res = await client.get("/api/v1/users/status", headers=auth_headers)
        status_data = res.json()
        if (
            res.status_code == 200
            and status_data.get("is_trial_active") is True
            and status_data.get("is_premium") is False
            and status_data.get("trial_remaining_seconds", 0) > 0
        ):
            log_pass(
                "GET /users/status - 200 OK",
                f"Trial remaining: {status_data.get('trial_remaining_seconds')}s, is_premium={status_data.get('is_premium')}"
            )
        else:
            log_fail("GET /users/status", f"Expected 200 with valid trial fields, got {res.status_code}: {res.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 5. PATCH /users/me/password - Wrong Old Password (401)
        # -------------------------------------------------------------
        res = await client.patch(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "old_password": "WrongPassword999!",
                "new_password": "NewValidPassword456!",
            },
        )
        if res.status_code == 401:
            log_pass("PATCH /users/me/password (Wrong Old Password) - 401 Unauthorized")
        else:
            log_fail("PATCH /users/me/password (Wrong Old)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 6. PATCH /users/me/password - Success (200 OK)
        # -------------------------------------------------------------
        new_password = "NewValidPassword456!"
        res = await client.patch(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "old_password": password,
                "new_password": new_password,
            },
        )
        if res.status_code == 200:
            log_pass("PATCH /users/me/password - 200 OK", "Password updated successfully")
        else:
            log_fail("PATCH /users/me/password", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False

        # Verify old password fails
        old_login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        if old_login.status_code == 401:
            log_pass("POST /auth/login (Old Password Rejected) - 401 Unauthorized")
        else:
            log_fail("POST /auth/login (Old Password)", f"Expected 401, got {old_login.status_code}")
            all_passed = False

        # Verify new password succeeds
        new_login = await client.post("/api/v1/auth/login", json={"email": email, "password": new_password})
        if new_login.status_code == 200:
            log_pass("POST /auth/login (New Password Accepted) - 200 OK")
        else:
            log_fail("POST /auth/login (New Password)", f"Expected 200, got {new_login.status_code}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_users_suite())
    sys.exit(0 if success else 1)
