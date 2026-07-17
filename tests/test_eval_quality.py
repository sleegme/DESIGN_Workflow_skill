from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from scripts import grade_semantic_results

ROOT = Path(__file__).resolve().parents[1]


class EvalQualityTests(unittest.TestCase):
    def test_every_route_has_multilingual_or_boundary_coverage(self) -> None:
        cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
        counts = Counter(case["expected_route"] for case in cases)
        self.assertTrue(all(count >= 5 for count in counts.values()))
        prompts = "\n".join(case["prompt"] for case in cases)
        self.assertIn("완전히", prompts)
        self.assertIn("entirely new", prompts)

    def test_trigger_negatives_are_near_misses(self) -> None:
        cases = json.loads((ROOT / "evals/trigger-cases.json").read_text(encoding="utf-8"))
        negatives = [case for case in cases if not case["should_trigger"]]
        categories = {case["category"] for case in negatives}
        self.assertIn("design-keyword-near-miss", categories)
        self.assertIn("file-conversion", categories)
        self.assertIn("language-translation", categories)
        self.assertGreaterEqual(len(negatives), 12)

    def test_partial_evidence_and_mixed_route_cases_exist(self) -> None:
        trigger_cases = json.loads((ROOT / "evals/trigger-cases.json").read_text(encoding="utf-8"))
        categories = {case["category"] for case in trigger_cases}
        self.assertIn("partial-evidence", categories)
        self.assertIn("mixed", categories)

    def test_semantic_grader_accepts_complete_matching_results(self) -> None:
        suite = json.loads((ROOT / "evals/semantic-smoke.json").read_text(encoding="utf-8"))
        result = {
            "runner": "unit-test",
            "skill_revision": "test",
            "cases": [
                {
                    "id": case["id"],
                    "observed_route": case["expected_route"],
                    "boundary_preserved": True,
                    "notes": "",
                }
                for case in suite
            ],
        }
        graded = grade_semantic_results.grade(suite, result)
        self.assertEqual(graded["summary"]["pass_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
