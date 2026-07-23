from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

from scripts import grade_semantic_results

ROOT = Path(__file__).resolve().parents[1]

CONTRACT_MODULE_PATH = ROOT / "design-workflow/scripts/validate_route_contract.py"
CONTRACT_SPEC = importlib.util.spec_from_file_location(
    "validate_route_contract", CONTRACT_MODULE_PATH
)
assert CONTRACT_SPEC and CONTRACT_SPEC.loader
CONTRACT_MODULE = importlib.util.module_from_spec(CONTRACT_SPEC)
CONTRACT_SPEC.loader.exec_module(CONTRACT_MODULE)


class EvalQualityTests(unittest.TestCase):
    def test_every_known_route_has_at_least_five_cases(self) -> None:
        cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
        counts = Counter(case["expected_route"] for case in cases)
        for route in sorted(CONTRACT_MODULE.ROUTES):
            with self.subTest(route=route):
                self.assertGreaterEqual(
                    counts.get(route, 0),
                    5,
                    f"route {route!r} is missing from routing-cases.json or has fewer than 5 cases",
                )

    def test_routing_cases_include_global_multilingual_sentinels(self) -> None:
        cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
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
            "schema_version": "1.0",
            "executed_at": "2026-07-20T12:00:00Z",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "skill_version": "0.2.1",
            "runner": "unit-test",
            "client": "unit-test-client",
            "model": "fixture-model",
            "reasoning_effort": "fixture",
            "suite_file": "evals/semantic-smoke.json",
            "suite_revision": "0123456789abcdef0123456789abcdef01234567",
            "cases": [
                {
                    "id": case["id"],
                    "observed_route": case["expected_route"],
                    "boundary_preserved": True,
                    "boundary_rationale": "Fixture rationale for schema validation.",
                    "notes": "",
                }
                for case in suite
            ],
        }
        graded = grade_semantic_results.grade(suite, result)
        self.assertEqual(graded["summary"]["pass_rate"], 1.0)
        self.assertTrue(graded["requires_independent_boundary_review"])
        self.assertEqual(graded["cases"][0]["expected_boundary"], suite[0]["expected_boundary"])

    def test_semantic_grader_requires_provenance_and_boundary_rationale(self) -> None:
        suite = json.loads((ROOT / "evals/semantic-smoke.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "schema_version is required"):
            grade_semantic_results.grade(suite, {"cases": []})

        result = {
            "schema_version": "1.0",
            "cases": [],
        }
        with self.assertRaisesRegex(ValueError, "executed_at"):
            grade_semantic_results.grade(suite, result)

        result = {
            "schema_version": "1.0",
            "executed_at": "2026-07-20T12:00:00Z",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "skill_version": "0.2.1",
            "runner": "unit-test",
            "model": "fixture-model",
            "reasoning_effort": "fixture",
            "suite_file": "evals/semantic-smoke.json",
            "suite_revision": "0123456789abcdef0123456789abcdef01234567",
            "cases": [
                {
                    "id": case["id"],
                    "observed_route": case["expected_route"],
                    "boundary_preserved": True,
                }
                for case in suite
            ],
        }
        with self.assertRaisesRegex(ValueError, "boundary_rationale"):
            grade_semantic_results.grade(suite, result)


if __name__ == "__main__":
    unittest.main()
