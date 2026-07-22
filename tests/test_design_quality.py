from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import grade_design_quality_results

ROOT = Path(__file__).resolve().parents[1]


class DesignQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = json.loads(
            (ROOT / "evals/design-quality-cases.json").read_text(encoding="utf-8")
        )

    def complete_result(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "executed_at": "2026-07-22T12:00:00+09:00",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "skill_version": "0.3.0",
            "client": "fixture-client",
            "runner": "unit-test",
            "model": "fixture-model",
            "reasoning_effort": "fixture",
            "suite_file": "evals/design-quality-cases.json",
            "suite_revision": "0123456789abcdef0123456789abcdef01234567",
            "evaluator": "fixture-reviewer",
            "cases": [
                {
                    "id": case["id"],
                    "baseline_artifact": f"fixture://baseline/{case['id']}",
                    "candidate_artifact": f"fixture://candidate/{case['id']}",
                    "observations": [
                        {
                            "property": property_name,
                            "result": "pass",
                            "evidence": "Fixture evidence used only to test record structure.",
                        }
                        for property_name in case["required_observations"]
                    ],
                }
                for case in self.suite
            ],
        }

    def test_suite_covers_required_scenarios_and_media(self) -> None:
        scenarios = {case["scenario"] for case in self.suite}
        self.assertEqual(
            scenarios,
            {
                "image-no-reference",
                "image-with-reference",
                "poster-card-news",
                "redesign-fixed-dimensions",
                "web-interface",
                "realistic-image",
            },
        )
        self.assertEqual(
            {case["medium"] for case in self.suite},
            {"generated-image", "editorial-social", "web-interface"},
        )

    def test_grader_accepts_complete_records_without_claiming_aesthetic_proof(self) -> None:
        graded = grade_design_quality_results.grade(self.suite, self.complete_result())
        self.assertEqual(graded["summary"]["declared_pass_rate"], 1.0)
        self.assertEqual(graded["result_type"], "structural_record_check")
        self.assertTrue(graded["requires_independent_visual_review"])
        self.assertFalse(graded["supports_universal_aesthetic_claim"])
        self.assertNotEqual(
            graded["cases"][0]["baseline_artifact"],
            graded["cases"][0]["candidate_artifact"],
        )

    def test_grader_rejects_missing_observation_or_evidence(self) -> None:
        result = self.complete_result()
        first_case = result["cases"][0]  # type: ignore[index]
        first_case["observations"].pop()  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "observation properties differ"):
            grade_design_quality_results.grade(self.suite, result)

        result = self.complete_result()
        first_case = result["cases"][0]  # type: ignore[index]
        first_case["observations"][0]["evidence"] = ""  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "evidence must be a non-empty string"):
            grade_design_quality_results.grade(self.suite, result)

    def test_runtime_requires_selective_loading_and_one_repair_pass(self) -> None:
        skill = (ROOT / "design-workflow/SKILL.md").read_text(encoding="utf-8")
        direction = (
            ROOT / "design-workflow/references/visual-direction.md"
        ).read_text(encoding="utf-8")
        self.assertIn("load exactly the one matching medium reference", skill)
        self.assertIn("same executing model must perform exactly one critique pass", direction)
        self.assertIn("Do not critique\nthe repaired result again", direction)
        self.assertIn("specific reason", direction)


if __name__ == "__main__":
    unittest.main()
