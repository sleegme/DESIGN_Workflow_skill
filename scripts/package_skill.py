#!/usr/bin/env python3
"""Build a deterministic release archive with design-workflow/ at its root."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "design-workflow"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
EXCLUDED_PARTS = {"__pycache__", ".DS_Store"}


def release_files() -> list[Path]:
    files = []
    for path in SKILL.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(SKILL).as_posix())


def write_archive(output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in release_files():
            relative = path.relative_to(SKILL).as_posix()
            info = zipfile.ZipInfo(f"design-workflow/{relative}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            archive.writestr(info, path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        if "design-workflow/SKILL.md" not in names:
            raise RuntimeError("archive is missing design-workflow/SKILL.md")
        if any(not name.startswith("design-workflow/") or ".." in Path(name).parts for name in names):
            raise RuntimeError("archive contains an invalid root or traversal path")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="semantic version, optionally prefixed with v")
    parser.add_argument("--output-dir", default="dist", help="directory for archive and checksum")
    args = parser.parse_args()

    version = args.version.removeprefix("v")
    if not VERSION_RE.fullmatch(version):
        parser.error("--version must be a semantic version such as 0.2.0")
    if not SKILL.is_dir():
        raise SystemExit("design-workflow directory does not exist")

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    archive = output_dir / f"design-workflow-{version}.zip"
    digest = write_archive(archive)
    print(json.dumps({"archive": str(archive), "sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
