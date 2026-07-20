from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath

from scripts import package_project, package_skill, validate_project


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


if __name__ == "__main__":
    unittest.main()
