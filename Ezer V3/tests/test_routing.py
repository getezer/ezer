"""
Ezer V3.2 — Route Determination Unit Tests
tests/test_routing.py

Tests the determine_rider_route() decision gate in isolation.
No settlement data. No report generation. Logic only.

Three scenarios:
  Scenario 1 — protector_rider: true          → Route A (Grievance)
  Scenario 2 — inactive + age flag present    → Route B (Gap Awareness)
  Scenario 3 — inactive + no age flag         → Route C (Renewal Action)
"""

import sys
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
from symmetry_report import determine_rider_route

# ── Mock Schedules ──────────────────────────────────────────────────────────────

SCENARIO_1 = {
    "addons_active": {
        "protector_rider": True
    }
}

SCENARIO_2 = {
    "addons_active": {
        "protector_rider": False,
        "rider_ineligible_due_to_age": {
            "protector_rider": "Informally unavailable — age 77 at renewal."
        }
    }
}

SCENARIO_3 = {
    "addons_active": {
        "protector_rider": False
    }
}

# ── Test Runner ─────────────────────────────────────────────────────────────────

def run_tests():
    W = 70
    print("\n" + "═" * W)
    print("  EZER V3.2 — ROUTE DETERMINATION UNIT TESTS")
    print("  tests/test_routing.py")
    print("═" * W)

    tests = [
        {
            "id":       1,
            "label":    "Protector Rider ACTIVE",
            "schedule": SCENARIO_1,
            "expected": "A",
            "expected_label": "Grievance Mode"
        },
        {
            "id":       2,
            "label":    "Rider INACTIVE + Age Flag Present",
            "schedule": SCENARIO_2,
            "expected": "B",
            "expected_label": "Gap Awareness Mode"
        },
        {
            "id":       3,
            "label":    "Rider INACTIVE + No Age Flag",
            "schedule": SCENARIO_3,
            "expected": "C",
            "expected_label": "Renewal Action Mode"
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        route, reason = determine_rider_route(test["schedule"])
        result = "PASS" if route == test["expected"] else "FAIL"

        icon = "✅" if result == "PASS" else "❌"
        print(f"\n  {icon} Scenario {test['id']} — {test['label']}")
        print(f"     Expected : Route {test['expected']} ({test['expected_label']})")
        print(f"     Got      : Route {route}")
        print(f"     Reason   : {reason[:65]}...")
        print(f"     Result   : {result}")

        if result == "PASS":
            passed += 1
        else:
            failed += 1

    print(f"\n  {'─' * (W-2)}")
    print(f"\n  Tests passed : {passed} / {len(tests)}")
    print(f"  Tests failed : {failed} / {len(tests)}")

    if failed == 0:
        print(f"\n  ✅ ALL TESTS PASSED — Decision gate is deterministic.")
        print(f"     Route A, B, C all trigger correctly.")
        print(f"     feature/v3.2-settlement-advocate branch is LOCKED.")
    else:
        print(f"\n  ❌ {failed} TEST(S) FAILED — Review routing logic.")

    print("\n" + "═" * W + "\n")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
