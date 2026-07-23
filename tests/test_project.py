from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath

from scripts import grade_design_quality_results, grade_semantic_results, package_project, package_skill, validate_project

RESULTS = validate_project.ROOT / "evals" / "results"


class ProjectTests(unittest.TestCase):
    def test_project_validator_passes(self) -> None:
        self.assertEqual(validate_project.main(), 0)

    def test_release_archive_is_deterministic_and_installable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.zip"
            second = Path(temp_dir) / "second.zip"
            first_hash = package_skill.write_archive(first)
            second_hash = package_skill.write_archive(second)
            self.assertEqual(first_hash, second_hash)
            self.assertEqual(first.read_bytes(), second.read_bytes())

            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
            self.assertIn("design-workflow/SKILL.md", names)
            self.assertIn("design-workflow/agents/openai.yaml", names)
            self.assertIn("design-workflow/references/visual-direction.md", names)
            self.assertIn("design-workflow/references/generated-image-design.md", names)
            self.assertIn("design-workflow/references/editorial-social-design.md", names)
            self.assertIn("design-workflow/references/web-interface-design.md", names)
            self.assertNotIn("design-workflow/references/frontend-design.md", names)
            self.assertTrue(all(name.startswith("design-workflow/") for name in names))
            self.assertFalse(any(name.endswith("README.md") for name in names))

    def test_release_file_allowlist_rejects_unsafe_fixtures(self) -> None:
        unsafe_paths = [
            "assets/.env",
            "assets/.env.production",
            "assets/draft.tmp",
            "assets/draft.bak",
            "assets/archive.zip",
            "assets/archive.zip.sha256",
            "assets/client-secret.json",
            "internal-notes.md",
        ]
        for unsafe in unsafe_paths:
            with self.subTest(path=unsafe), tempfile.TemporaryDirectory() as temp_dir:
                skill = Path(temp_dir) / "design-workflow"
                safe = skill / "assets/safe.json"
                safe.parent.mkdir(parents=True)
                safe.write_text("{}\n", encoding="utf-8")
                target = skill / unsafe
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture only\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    package_skill.release_files(skill)

    def test_release_file_allowlist_excludes_python_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = Path(temp_dir) / "design-workflow"
            safe = skill / "scripts/validate.py"
            cache = skill / "scripts/__pycache__/validate.cpython-311.pyc"
            safe.parent.mkdir(parents=True)
            cache.parent.mkdir(parents=True)
            safe.write_text("pass\n", encoding="utf-8")
            cache.write_bytes(b"not a real cache")
            self.assertEqual(package_skill.release_files(skill), [safe])

    def test_release_file_allowlist_rejects_oversized_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = Path(temp_dir) / "design-workflow"
            oversized = skill / "assets/oversized.json"
            oversized.parent.mkdir(parents=True)
            oversized.write_bytes(b"x" * (package_skill.MAX_RELEASE_FILE_SIZE + 1))
            with self.assertRaisesRegex(ValueError, "exceeds"):
                package_skill.release_files(skill)

    def test_release_file_allowlist_rejects_symlinks_and_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = Path(temp_dir) / "design-workflow"
            reference = skill / "references/routing.md"
            reference.parent.mkdir(parents=True)
            reference.write_text("safe\n", encoding="utf-8")
            (skill / "references/linked.md").symlink_to(reference)
            with self.assertRaises(ValueError):
                package_skill.release_files(skill)
        with self.assertRaises(ValueError):
            package_skill._validate_relative_path(PurePosixPath("../secret.txt"))

    def test_package_versions_default_to_version_file_and_reject_mismatch(self) -> None:
        expected = (package_skill.ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(package_skill.resolve_version(None), expected)
        self.assertEqual(package_skill.resolve_version(f"v{expected}"), expected)
        self.assertEqual(package_project.resolve_version(None), expected)
        with self.assertRaisesRegex(ValueError, "does not match VERSION"):
            package_skill.resolve_version("0.2.0")
        with self.assertRaisesRegex(ValueError, "does not match VERSION"):
            package_project.resolve_version("0.2.0")

    def test_workflows_read_version_and_release_checks_tag(self) -> None:
        root = package_skill.ROOT
        ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        release = (root / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn("version=$(<VERSION)", ci)
        self.assertIn("python scripts/package_skill.py --output-dir", ci)
        self.assertNotIn("0.2.0", ci)
        self.assertIn("version=$(<VERSION)", release)
        self.assertIn('"$GITHUB_REF_NAME" != "v${version}"', release)
        self.assertIn('package_skill.py --version "$GITHUB_REF_NAME"', release)
        self.assertIn('gh release view "$GITHUB_REF_NAME"', release)
        self.assertIn('gh release upload "$GITHUB_REF_NAME"', release)
        self.assertIn("--clobber", release)

    def test_project_archive_contains_source_without_git_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "project.zip"
            version = package_project.read_version()
            package_project.write_archive(archive_path, version)
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
            prefix = f"design-workflow-project-{version}/"
            self.assertIn(f"{prefix}README.md", names)
            self.assertIn(f"{prefix}design-workflow/SKILL.md", names)
            self.assertFalse(any("/.git/" in name or "/dist/" in name for name in names))


def _base_routing_cases() -> list[dict[str, object]]:
    """A synthetic routing-cases fixture that satisfies every existing invariant.

    Each of the eight routes appears six times, with the field values that the
    repository's own routing-cases.json already uses. The fixture is intentionally
    self-contained so that the Issue #14 regression tests can mutate one field at
    a time without reaching into the real committed fixture.
    """
    route_values: dict[str, dict[str, object]] = {
        "preserve": {"meaningful_design_exists": True, "mutates_artifact": True, "redesign_authorized": False},
        "expand": {"meaningful_design_exists": True, "mutates_artifact": True, "redesign_authorized": False},
        "create": {"meaningful_design_exists": False, "mutates_artifact": True, "redesign_authorized": False},
        "redesign": {"meaningful_design_exists": True, "mutates_artifact": True, "redesign_authorized": True},
        "critique": {"meaningful_design_exists": True, "mutates_artifact": False, "redesign_authorized": False},
        "brand-check": {"meaningful_design_exists": True, "mutates_artifact": False, "redesign_authorized": False},
        "translate": {"meaningful_design_exists": True, "mutates_artifact": True, "redesign_authorized": False},
        "profile": {"meaningful_design_exists": True, "mutates_artifact": False, "redesign_authorized": False},
    }
    cases: list[dict[str, object]] = []
    for route, values in route_values.items():
        for index in range(6):
            cases.append(
                {
                    "id": f"{route.upper()[:3]}.{index}",
                    "prompt": f"synthetic prompt {route} {index}",
                    "expected_route": route,
                    "basis": "synthetic basis",
                    **values,
                }
            )
    return cases


class RouteCaseValidationTests(unittest.TestCase):
    """Issue #14: route-case boolean fields and route contracts are strictly enforced."""

    def _run_with_cases(self, cases: list[dict[str, object]]) -> None:
        path = validate_project.ROOT / "evals" / "routing-cases.json"
        backup = path.read_text(encoding="utf-8")
        try:
            path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            validate_project.validate_route_cases()
        finally:
            path.write_text(backup, encoding="utf-8")

    def _expect_failure(self, cases: list[dict[str, object]]) -> str:
        path = validate_project.ROOT / "evals" / "routing-cases.json"
        backup = path.read_text(encoding="utf-8")
        try:
            path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(validate_project.ValidationError) as ctx:
                validate_project.validate_route_cases()
            return str(ctx.exception)
        finally:
            path.write_text(backup, encoding="utf-8")

    def test_committed_routing_cases_fixture_is_valid(self) -> None:
        validate_project.validate_route_cases()

    def test_synthetic_base_fixture_is_valid(self) -> None:
        self._run_with_cases(_base_routing_cases())

    def test_string_mutates_artifact_is_rejected(self) -> None:
        cases = _base_routing_cases()
        cases[0]["mutates_artifact"] = "true"
        message = self._expect_failure(cases)
        self.assertIn(cases[0]["id"], message)
        self.assertIn("mutates_artifact", message)
        self.assertIn("bool", message)

    def test_integer_mutates_artifact_is_rejected(self) -> None:
        cases = _base_routing_cases()
        cases[0]["mutates_artifact"] = 1
        message = self._expect_failure(cases)
        self.assertIn(cases[0]["id"], message)
        self.assertIn("mutates_artifact", message)
        self.assertIn("bool", message)

    def test_string_redesign_authorized_is_rejected(self) -> None:
        cases = _base_routing_cases()
        cases[0]["redesign_authorized"] = "false"
        message = self._expect_failure(cases)
        self.assertIn(cases[0]["id"], message)
        self.assertIn("redesign_authorized", message)
        self.assertIn("bool", message)

    def test_integer_redesign_authorized_is_rejected(self) -> None:
        cases = _base_routing_cases()
        cases[0]["redesign_authorized"] = 0
        message = self._expect_failure(cases)
        self.assertIn(cases[0]["id"], message)
        self.assertIn("redesign_authorized", message)
        self.assertIn("bool", message)

    def test_mutating_routes_reject_mutates_artifact_false(self) -> None:
        mutating = ["preserve", "expand", "create", "redesign", "translate"]
        for route in mutating:
            with self.subTest(route=route):
                cases = _base_routing_cases()
                target = next(case for case in cases if case["expected_route"] == route)
                target["mutates_artifact"] = False
                message = self._expect_failure(cases)
                self.assertIn(target["id"], message)
                self.assertIn(route, message)
                self.assertIn("mutates_artifact", message)

    def test_non_mutating_routes_reject_mutates_artifact_true(self) -> None:
        non_mutating = ["critique", "brand-check", "profile"]
        for route in non_mutating:
            with self.subTest(route=route):
                cases = _base_routing_cases()
                target = next(case for case in cases if case["expected_route"] == route)
                target["mutates_artifact"] = True
                message = self._expect_failure(cases)
                self.assertIn(target["id"], message)
                self.assertIn(route, message)
                self.assertIn("mutates_artifact", message)


class GradedResultIntegrityTests(unittest.TestCase):
    """Issue #13: committed graded result cases must exactly match recomputed grading."""

    def _semantic_suite(self) -> list[dict[str, object]]:
        return json.loads(
            (validate_project.ROOT / "evals" / "semantic-smoke.json").read_text(encoding="utf-8")
        )

    def _design_quality_suite(self) -> list[dict[str, object]]:
        return json.loads(
            (validate_project.ROOT / "evals" / "design-quality-cases.json").read_text(encoding="utf-8")
        )

    def _semantic_complete_raw(self, suite: list[dict[str, object]]) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "executed_at": "2026-07-22T12:00:00+09:00",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "skill_version": "0.3.0",
            "client": "unit-test-client",
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
                    "boundary_rationale": "Fixture rationale used only to test record structure.",
                    "response_excerpt": "",
                    "notes": "",
                }
                for case in suite
            ],
        }

    def _design_quality_complete_raw(self, suite: list[dict[str, object]]) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "executed_at": "2026-07-22T12:00:00+09:00",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "skill_version": "0.3.0",
            "client": "unit-test-client",
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
                for case in suite
            ],
        }

    def test_validators_accept_untampered_committed_results(self) -> None:
        validate_project.validate_semantic_evidence()
        validate_project.validate_design_quality_evidence()

    def test_semantic_validator_detects_per_case_tampering_with_unchanged_summary(self) -> None:
        graded_path = RESULTS / "v0.2.0-codex-forward-test.json"
        backup = graded_path.read_text(encoding="utf-8")
        try:
            graded = json.loads(backup)
            graded["cases"][0]["observed_route"] = "redesign"
            graded_path.write_text(json.dumps(graded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(validate_project.ValidationError):
                validate_project.validate_semantic_evidence()
        finally:
            graded_path.write_text(backup, encoding="utf-8")

    def test_semantic_validator_detects_missing_deterministic_field(self) -> None:
        suite = self._semantic_suite()
        raw = self._semantic_complete_raw(suite)
        graded = grade_semantic_results.grade(suite, raw)
        raw_name = "v0.3.0-unit-test-forward-test.raw.json"
        graded_name = "v0.3.0-unit-test-forward-test.json"
        raw_path = RESULTS / raw_name
        graded_path = RESULTS / graded_name
        try:
            raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            graded_path.write_text(json.dumps(graded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            validate_project.validate_semantic_evidence()

            tampered = json.loads(graded_path.read_text(encoding="utf-8"))
            del tampered["cases"][0]["expected_boundary"]
            graded_path.write_text(json.dumps(tampered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(validate_project.ValidationError):
                validate_project.validate_semantic_evidence()
        finally:
            for path in (raw_path, graded_path):
                if path.exists():
                    path.unlink()

    def test_design_quality_validator_detects_per_case_tampering_with_unchanged_summary(self) -> None:
        suite = self._design_quality_suite()
        raw = self._design_quality_complete_raw(suite)
        graded = grade_design_quality_results.grade(suite, raw)
        raw_name = "v0.3.0-unit-test-design-quality.raw.json"
        graded_name = "v0.3.0-unit-test-design-quality.json"
        raw_path = RESULTS / raw_name
        graded_path = RESULTS / graded_name
        try:
            raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            graded_path.write_text(json.dumps(graded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            validate_project.validate_design_quality_evidence()

            tampered = json.loads(graded_path.read_text(encoding="utf-8"))
            tampered["cases"][0]["baseline_artifact"] = "fixture://tampered/DQ01"
            graded_path.write_text(json.dumps(tampered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(validate_project.ValidationError):
                validate_project.validate_design_quality_evidence()
        finally:
            for path in (raw_path, graded_path):
                if path.exists():
                    path.unlink()

    def test_design_quality_validator_detects_missing_deterministic_field(self) -> None:
        suite = self._design_quality_suite()
        raw = self._design_quality_complete_raw(suite)
        graded = grade_design_quality_results.grade(suite, raw)
        raw_name = "v0.3.0-unit-test-design-quality.raw.json"
        graded_name = "v0.3.0-unit-test-design-quality.json"
        raw_path = RESULTS / raw_name
        graded_path = RESULTS / graded_name
        try:
            raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            graded_path.write_text(json.dumps(graded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            validate_project.validate_design_quality_evidence()

            tampered = json.loads(graded_path.read_text(encoding="utf-8"))
            del tampered["cases"][0]["baseline_artifact"]
            graded_path.write_text(json.dumps(tampered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(validate_project.ValidationError):
                validate_project.validate_design_quality_evidence()
        finally:
            for path in (raw_path, graded_path):
                if path.exists():
                    path.unlink()


if __name__ == "__main__":
    unittest.main()
