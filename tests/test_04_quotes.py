"""Quote domain test suite.

Validates all routes under `/api/v1/quotes`:
- GET /quotes/today (Current UTC day-of-year motivational quote)
- GET /quotes/random (Random active motivational quote)
- GET /quotes/batch (Offline sync range queries, single day queries, boundary checks)
- Query parameter validation (ge=1, le=365, string validation -> 422 Unprocessable Entity)
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.config import get_test_client, print_header, log_pass, log_fail


async def test_quotes_suite() -> bool:
    """Runs all quote delivery and batch caching tests sequentially.

    Returns:
        True if all tests in the suite passed, False otherwise.
    """
    print_header("TEST SUITE 4: QUOTES & BATCH CACHING (/api/v1/quotes)")
    all_passed = True

    async with get_test_client() as client:
        # -------------------------------------------------------------
        # 1. GET /api/v1/quotes/today
        # -------------------------------------------------------------
        res_today = await client.get("/api/v1/quotes/today")
        if res_today.status_code == 200:
            data = res_today.json()
            if "content" in data and "author" in data and "day_number" in data:
                log_pass("GET /quotes/today", f"200 OK - Day {data['day_number']} by '{data['author']}'")
            else:
                log_fail("GET /quotes/today", f"Missing required fields: {data}")
                all_passed = False
        else:
            log_fail("GET /quotes/today", f"Expected 200, got {res_today.status_code}: {res_today.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 2. GET /api/v1/quotes/random
        # -------------------------------------------------------------
        res_random = await client.get("/api/v1/quotes/random")
        if res_random.status_code == 200:
            data = res_random.json()
            if "content" in data and "author" in data and "day_number" in data:
                log_pass("GET /quotes/random", f"200 OK - Day {data['day_number']} by '{data['author']}'")
            else:
                log_fail("GET /quotes/random", f"Missing required fields: {data}")
                all_passed = False
        else:
            log_fail("GET /quotes/random", f"Expected 200, got {res_random.status_code}: {res_random.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 3. GET /api/v1/quotes/batch (Valid 7-day range: 1..7)
        # -------------------------------------------------------------
        res_batch7 = await client.get("/api/v1/quotes/batch", params={"start_day": 1, "end_day": 7})
        if res_batch7.status_code == 200:
            quotes = res_batch7.json()
            if isinstance(quotes, list) and len(quotes) == 7:
                days = [q["day_number"] for q in quotes]
                if days == list(range(1, 8)):
                    log_pass("GET /quotes/batch (1..7)", f"200 OK - Retrieved exact sequence: {days}")
                else:
                    log_fail("GET /quotes/batch (1..7)", f"Unexpected day sequence: {days}")
                    all_passed = False
            else:
                log_fail("GET /quotes/batch (1..7)", f"Expected 7 quotes, got {len(quotes) if isinstance(quotes, list) else quotes}")
                all_passed = False
        else:
            log_fail("GET /quotes/batch (1..7)", f"Expected 200, got {res_batch7.status_code}: {res_batch7.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 4. GET /api/v1/quotes/batch (Single day range: 100..100)
        # -------------------------------------------------------------
        res_batch_single = await client.get("/api/v1/quotes/batch", params={"start_day": 100, "end_day": 100})
        if res_batch_single.status_code == 200:
            quotes = res_batch_single.json()
            if isinstance(quotes, list) and len(quotes) == 1 and quotes[0]["day_number"] == 100:
                log_pass("GET /quotes/batch (100..100)", "200 OK - Single day exact match confirmed")
            else:
                log_fail("GET /quotes/batch (100..100)", f"Expected 1 quote with day=100, got: {quotes}")
                all_passed = False
        else:
            log_fail("GET /quotes/batch (100..100)", f"Expected 200, got {res_batch_single.status_code}: {res_batch_single.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 5. GET /api/v1/quotes/batch (Validation: start_day < 1 -> 422)
        # -------------------------------------------------------------
        res_v1 = await client.get("/api/v1/quotes/batch", params={"start_day": 0, "end_day": 10})
        if res_v1.status_code == 422:
            log_pass("GET /quotes/batch (start_day=0)", "422 Unprocessable Entity - Lower bound ge=1 enforced")
        else:
            log_fail("GET /quotes/batch (start_day=0)", f"Expected 422, got {res_v1.status_code}: {res_v1.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 6. GET /api/v1/quotes/batch (Validation: end_day > 365 -> 422)
        # -------------------------------------------------------------
        res_v2 = await client.get("/api/v1/quotes/batch", params={"start_day": 1, "end_day": 366})
        if res_v2.status_code == 422:
            log_pass("GET /quotes/batch (end_day=366)", "422 Unprocessable Entity - Upper bound le=365 enforced")
        else:
            log_fail("GET /quotes/batch (end_day=366)", f"Expected 422, got {res_v2.status_code}: {res_v2.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 7. GET /api/v1/quotes/batch (Validation: Missing parameters -> 422)
        # -------------------------------------------------------------
        res_v3 = await client.get("/api/v1/quotes/batch")
        if res_v3.status_code == 422:
            log_pass("GET /quotes/batch (missing params)", "422 Unprocessable Entity - Required query parameters enforced")
        else:
            log_fail("GET /quotes/batch (missing params)", f"Expected 422, got {res_v3.status_code}: {res_v3.text}")
            all_passed = False

        # -------------------------------------------------------------
        # 8. GET /api/v1/quotes/batch (Validation: Non-integer parameter -> 422)
        # -------------------------------------------------------------
        res_v4 = await client.get("/api/v1/quotes/batch", params={"start_day": "not_an_int", "end_day": 10})
        if res_v4.status_code == 422:
            log_pass("GET /quotes/batch (invalid type)", "422 Unprocessable Entity - Integer type constraint enforced")
        else:
            log_fail("GET /quotes/batch (invalid type)", f"Expected 422, got {res_v4.status_code}: {res_v4.text}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    passed = asyncio.run(test_quotes_suite())
    sys.exit(0 if passed else 1)
