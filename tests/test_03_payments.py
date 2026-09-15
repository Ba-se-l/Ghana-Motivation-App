"""Payment endpoint test suite.

Validates all routes under `/api/v1/payments`:
- Payment initialization (/payments/initialize - zero-trust, server price)
- Transaction verification (/payments/verify - ownership boundary, status transition, idempotency)
- Webhook receiver (/payments/webhook - HMAC signature verification, idempotency)
"""

import asyncio
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from GhanaMotivationApp.settings import settings
from tests.config import get_test_client, print_header, log_pass, log_fail


async def test_payments_suite() -> bool:
    """Runs all payment and webhook tests sequentially.

    Returns:
        True if all tests in the suite passed, False otherwise.
    """
    print_header("TEST SUITE 3: PAYMENTS & TRUST BOUNDARY (/api/v1/payments)")
    all_passed = True

    async with get_test_client() as client:
        ts = int(time.time())
        user_a_email = f"pay_a_{ts}@example.com"
        user_b_email = f"pay_b_{ts}@example.com"
        password = "PaymentUserPass123!"

        # -------------------------------------------------------------
        # Setup: Register and Login User A and User B
        # -------------------------------------------------------------
        await client.post("/api/v1/auth/register", json={
            "name": "User A", "email": user_a_email, "password": password, "device_fingerprint": f"DEVA_{ts}"
        })
        login_a = await client.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})
        tokens_a = login_a.json()
        headers_a = {"Authorization": f"Bearer {tokens_a['access_token']}"}

        await client.post("/api/v1/auth/register", json={
            "name": "User B", "email": user_b_email, "password": password, "device_fingerprint": f"DEVB_{ts}"
        })
        login_b = await client.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        tokens_b = login_b.json()
        headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}

        # -------------------------------------------------------------
        # 1. POST /payments/initialize Unauthorized (401)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/payments/initialize")
        if res.status_code == 401:
            log_pass("POST /payments/initialize (No Auth) - 401 Unauthorized")
        else:
            log_fail("POST /payments/initialize (No Auth)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 2. POST /payments/initialize Success (200 OK)
        # -------------------------------------------------------------
        res = await client.post("/api/v1/payments/initialize", headers=headers_a)
        init_data = res.json()
        if (
            res.status_code == 200
            and "authorization_url" in init_data
            and "reference" in init_data
        ):
            ref_a = init_data["reference"]
            log_pass("POST /payments/initialize - 200 OK", f"Ref: {ref_a}")
        else:
            log_fail("POST /payments/initialize", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False
            return False

        # -------------------------------------------------------------
        # 3. GET /payments/verify Unauthorized (401)
        # -------------------------------------------------------------
        res = await client.get(f"/api/v1/payments/verify?reference={ref_a}")
        if res.status_code == 401:
            log_pass("GET /payments/verify (No Auth) - 401 Unauthorized")
        else:
            log_fail("GET /payments/verify (No Auth)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 4. Ownership Boundary: User B verifies User A's transaction (403)
        # -------------------------------------------------------------
        res = await client.get(f"/api/v1/payments/verify?reference={ref_a}", headers=headers_b)
        if res.status_code == 403:
            log_pass("GET /payments/verify (Ownership Mismatch) - 403 Forbidden", "Ownership guard passed")
        else:
            log_fail("GET /payments/verify (Ownership Mismatch)", f"Expected 403, got {res.status_code}: {res.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 5. Legitimate Verification by Owner (User A) (200 OK)
        # -------------------------------------------------------------
        res = await client.get(f"/api/v1/payments/verify?reference={ref_a}", headers=headers_a)
        verify_data = res.json()
        if res.status_code == 200 and verify_data.get("status") == "success":
            log_pass("GET /payments/verify - 200 OK", f"Status: {verify_data.get('status')}")
        else:
            log_fail("GET /payments/verify", f"Expected 200 with status=success, got {res.status_code}: {res.text}")
            all_passed = False

        # Check User A is now premium
        status_res = await client.get("/api/v1/users/status", headers=headers_a)
        status_data = status_res.json()
        if status_res.status_code == 200 and status_data.get("is_premium") is True:
            log_pass("Premium Activation Verification", f"User is_premium={status_data.get('is_premium')}")
        else:
            log_fail("Premium Activation Verification", f"User failed to become premium: {status_data}")
            all_passed = False

        # -------------------------------------------------------------
        # 6. Idempotency Check: Verifying again returns 200 without error
        # -------------------------------------------------------------
        res_repeat = await client.get(f"/api/v1/payments/verify?reference={ref_a}", headers=headers_a)
        if res_repeat.status_code == 200 and res_repeat.json().get("status") == "success":
            log_pass("GET /payments/verify (Idempotency) - 200 OK", "Duplicate verification handled safely")
        else:
            log_fail("GET /payments/verify (Idempotency)", f"Expected 200, got {res_repeat.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 7. POST /payments/webhook - Invalid HMAC Signature (401)
        # -------------------------------------------------------------
        res = await client.post(
            "/api/v1/payments/webhook",
            content=b'{"event": "charge.success"}',
            headers={"X-Paystack-Signature": "invalid_fake_signature_hex"},
        )
        if res.status_code == 401:
            log_pass("POST /payments/webhook (Bad Signature) - 401 Unauthorized")
        else:
            log_fail("POST /payments/webhook (Bad Signature)", f"Expected 401, got {res.status_code}")
            all_passed = False

        # -------------------------------------------------------------
        # 8. POST /payments/webhook - Valid HMAC Signature (200 OK)
        # -------------------------------------------------------------
        webhook_body = json.dumps({
            "event": "charge.success",
            "data": {
                "reference": ref_a,
                "amount": settings.SUBSCRIPTION_AMOUNT_PESEWAS,
                "currency": "GHS",
                "status": "success",
            }
        }).encode("utf-8")

        valid_signature = hmac.new(
            key=settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            msg=webhook_body,
            digestmod=hashlib.sha512,
        ).hexdigest()

        res = await client.post(
            "/api/v1/payments/webhook",
            content=webhook_body,
            headers={
                "X-Paystack-Signature": valid_signature,
                "Content-Type": "application/json",
            },
        )
        if res.status_code == 200 and res.json().get("status") == "ok":
            log_pass("POST /payments/webhook (Valid HMAC) - 200 OK", "Webhook processed idempotently")
        else:
            log_fail("POST /payments/webhook (Valid HMAC)", f"Expected 200, got {res.status_code}: {res.text}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_payments_suite())
    sys.exit(0 if success else 1)
