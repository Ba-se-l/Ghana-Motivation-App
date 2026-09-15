"""Authentication endpoint test suite.

Validates all routes under `/api/v1/auth`:
- Registration (happy path, duplicate email, validation errors)
- Login (valid credentials, wrong password, non-existent user)
- Token Rotation (refresh token exchange, revoked token reuse detection)
- Logout (single device session revocation, all devices bulk revocation)
"""
import sys
import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.config import get_test_client, print_header, log_pass, log_fail


async def test_auth_suite() -> bool:
    """Runs all authentication tests sequentially.

    Returns:
        True if all tests in the suite passed, False otherwise.
    """
    print_header("TEST SUITE 1: AUTHENTICATION (/api/v1/auth)")
    all_passed = True

    async with get_test_client() as client:
        ts = int(time.time())
        email = f"authtest_{ts}@example.com"
        password = "SecurePassword123!"

        # -------------------------------------------------------------
        # 1. Register Success
        # -------------------------------------------------------------
        reg_payload = {
            "name": "Auth Tester",
            "email": email,
            "password": password,
            "device_fingerprint": f"FINGERPRINT_{ts}",
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        if res.status_code == 201 and res.json().get("email") == email:
            log_pass("POST /auth/register - 201 Created", f"User ID: {res.json().get('id')}")
        else:
            log_fail("POST /auth/register", f"Expected 201, got {res.status_code}: {res.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 2. Register Duplicate Email (409 Conflict)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        if res.status_code == 409:
            log_pass("POST /auth/register (Duplicate) - 409 Conflict", res.json().get("error_code", ""))
        else:
            log_fail("POST /auth/register (Duplicate)", f"Expected 409, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 3. Register Validation Error (422)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/register", json={
            "name": "",
            "email": "not-an-email",
            "password": "short",
            "device_fingerprint": "x",
        })
        if res.status_code == 422:
            log_pass("POST /auth/register (Invalid Input) - 422 Unprocessable Entity")
        else:
            log_fail("POST /auth/register (Invalid Input)", f"Expected 422, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 4. Login Success (200 OK)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password,
        })
        tokens = res.json()
        if res.status_code == 200 and "access_token" in tokens and "refresh_token" in tokens:
            log_pass("POST /auth/login - 200 OK", "Dual token pair issued")
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
        else:
            log_fail("POST /auth/login", f"Expected 200 with tokens, got {res.status_code}: {res.text}")
            all_passed = False
            return False

        # -------------------------------------------------------------
        # 5. Login Wrong Password (401 Unauthorized)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "IncorrectPassword999!",
        })
        if res.status_code == 401:
            log_pass("POST /auth/login (Wrong Password) - 401 Unauthorized")
        else:
            log_fail("POST /auth/login (Wrong Password)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 6. Login Non-Existent User (401 Unauthorized)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/login", json={
            "email": "does_not_exist_xyz@example.com",
            "password": password,
        })
        if res.status_code == 401:
            log_pass("POST /auth/login (Non-Existent User) - 401 Unauthorized")
        else:
            log_fail("POST /auth/login (Non-Existent User)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 7. Refresh Token Rotation (200 OK)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        new_tokens = res.json()
        if res.status_code == 200 and "access_token" in new_tokens and "refresh_token" in new_tokens:
            log_pass("POST /auth/refresh - 200 OK", "New token pair issued (Rotation verified)")
            new_refresh_token = new_tokens["refresh_token"]
        else:
            log_fail("POST /auth/refresh", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False
            new_refresh_token = refresh_token

        # -------------------------------------------------------------
        # 8. Reusing Revoked Token Triggers Theft Guard (401 Unauthorized)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        if res.status_code == 401:
            log_pass("POST /auth/refresh (Reused Token) - 401 Unauthorized", "Theft guard triggered")
        else:
            log_fail("POST /auth/refresh (Reused Token)", f"Expected 401 for revoked token, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 9. Logout Current Device (200 OK)
        # -------------------------------------------------------------
        # Issue fresh login session to test logout
        res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        logout_session_tokens = res.json()
        active_refresh_token = logout_session_tokens.get("refresh_token")

        res = await client.post("/api/v1/auth/logout", json={"refresh_token": active_refresh_token})
        if res.status_code == 200:
            log_pass("POST /auth/logout - 200 OK", "Single device session revoked")
        else:
            log_fail("POST /auth/logout", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False

        # Verify the logged out token is revoked
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": active_refresh_token})
        if res.status_code == 401:
            log_pass("POST /auth/refresh (Post-Logout) - 401 Unauthorized", "Revocation verified")
        else:
            log_fail("POST /auth/refresh (Post-Logout)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 10. Logout All Devices (200 OK)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        fresh_tokens = res.json()
        headers = {"Authorization": f"Bearer {fresh_tokens['access_token']}"}

        res = await client.post("/api/v1/auth/logout-all", headers=headers)
        if res.status_code == 200:
            log_pass("POST /auth/logout-all - 200 OK", "All sessions revoked for user")
        else:
            log_fail("POST /auth/logout-all", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_auth_suite())
    sys.exit(0 if success else 1)
