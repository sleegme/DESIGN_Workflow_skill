#!/usr/bin/env python3
"""Build a deterministic source archive for the complete project."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
EXCLUDED_DIRS = {".git", ".venv", ".tooling", "__pycache__", "dist"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip", ".sha256"}


def read_version() -> str:
    try:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError(f"cannot read VERSION: {exc}") from exc
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"VERSION must contain a semantic version, got {version!r}")
    return version


def resolve_version(requested: str | None) -> str:
    expected = read_version()
    if requested is None:
        return expected
    version = requested.removeprefix("v")
    if not VERSION_RE.fullmatch(version):
        raise ValueError("--version must be a semantic version such as 1.2.3")
    if version != expected:
        raise ValueError(
            f"--version {version!r} does not match VERSION {expected!r}"
        )
    return version


def project_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS or part.startswith("dist-") for part in relative.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def write_archive(output: Path, version: str | None = None) -> str:
    version = resolve_version(version)
    prefix = f"design-workflow-project-{version}"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in project_files():
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{relative}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            archive.writestr(info, path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        required = f"{prefix}/design-workflow/SKILL.md"
        if required not in names:
            raise RuntimeError(f"archive is missing {required}")
        if any(not name.startswith(f"{prefix}/") or ".." in Path(name).parts for name in names):
            raise RuntimeError("project archive contains an invalid path")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        help="semantic version, optionally prefixed with v; defaults to VERSION and must match it",
    )
    parser.add_argument("--output-dir", default="dist", help="directory for archive and checksum")
    args = parser.parse_args()

    try:
        version = resolve_version(args.version)
    except ValueError as exc:
        parser.error(str(exc))
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    archive = output_dir / f"design-workflow-project-{version}.zip"
    digest = write_archive(archive, version)
    print(json.dumps({"archive": str(archive), "sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
