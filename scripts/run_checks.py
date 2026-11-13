"""Execute deterministic synthetic tests and save honest observed results."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    start = time.perf_counter()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    summary = {"evaluation_type": "synthetic_unit_tests_only",
               "note": "Not a live API integration test, not a manual baseline, and not real-user validation.",
               "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "passed": result.testsRun - len(result.failures) - len(result.errors),
               "elapsed_seconds": round(time.perf_counter() - start, 4), "all_pass": result.wasSuccessful()}
    output = ROOT / "evaluation" / "observed_unit_tests.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("\nObserved test results saved to", output)
    sys.exit(0 if result.wasSuccessful() else 1)
