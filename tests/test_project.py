from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

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

    def test_project_archive_contains_source_without_git_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "project.zip"
            package_project.write_archive(archive_path, "0.2.0")
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
            prefix = "design-workflow-project-0.2.0/"
            self.assertIn(f"{prefix}README.md", names)
            self.assertIn(f"{prefix}design-workflow/SKILL.md", names)
            self.assertFalse(any("/.git/" in name or "/dist/" in name for name in names))


if __name__ == "__main__":
    unittest.main()
