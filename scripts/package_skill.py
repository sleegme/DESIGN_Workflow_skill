#!/usr/bin/env python3
"""Build a deterministic release archive with design-workflow/ at its root."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "design-workflow"
VERSION_FILE = ROOT / "VERSION"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
ROOT_FILES = {"SKILL.md", "LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"}
DIRECTORY_SUFFIXES = {
    "agents": {".yaml", ".yml"},
    "references": {".md"},
    "assets": {".json", ".md"},
    "scripts": {".py"},
}
DENIED_SUFFIXES = {
    ".bak",
    ".backup",
    ".orig",
    ".pyc",
    ".pyo",
    ".rej",
    ".sha256",
    ".swo",
    ".swp",
    ".temp",
    ".tmp",
    ".zip",
}
SENSITIVE_NAME_RE = re.compile(
    r"(?:^|[-_.])(access[-_]?key|api[-_]?key|credentials?|passwords?|passwd|"
    r"private[-_]?key|secrets?|tokens?)(?:$|[-_.])",
    re.IGNORECASE,
)
MAX_RELEASE_FILE_SIZE = 5 * 1024 * 1024


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
        raise ValueError("--version must be a semantic version such as 0.2.1")
    if version != expected:
        raise ValueError(
            f"--version {version!r} does not match VERSION {expected!r}"
        )
    return version


def _validate_relative_path(relative: PurePosixPath) -> None:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"unsafe release path: {relative}")
    if any(part.startswith(".") for part in relative.parts):
        raise ValueError(f"hidden release path is not allowed: {relative}")


def _validate_release_file(path: Path, skill: Path) -> None:
    relative = PurePosixPath(path.relative_to(skill).as_posix())
    _validate_relative_path(relative)
    top = relative.parts[0]
    if len(relative.parts) == 1:
        if top not in ROOT_FILES:
            raise ValueError(f"unexpected top-level release file: {relative}")
    elif top not in DIRECTORY_SUFFIXES:
        raise ValueError(f"unexpected release directory: {relative}")

    lower_name = relative.name.lower()
    if lower_name == ".env" or lower_name.startswith(".env."):
        raise ValueError(f"environment file is not allowed: {relative}")
    if lower_name.endswith("~") or any(lower_name.endswith(suffix) for suffix in DENIED_SUFFIXES):
        raise ValueError(f"temporary, cache, or archive file is not allowed: {relative}")
    if SENSITIVE_NAME_RE.search(lower_name) or lower_name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}:
        raise ValueError(f"credential-like file name is not allowed: {relative}")
    if len(relative.parts) > 1 and path.suffix.lower() not in DIRECTORY_SUFFIXES[top]:
        raise ValueError(f"unexpected file type in {top}/: {relative}")
    if path.stat().st_size > MAX_RELEASE_FILE_SIZE:
        raise ValueError(f"release file exceeds {MAX_RELEASE_FILE_SIZE} bytes: {relative}")


def release_files(skill: Path = SKILL) -> list[Path]:
    files: list[Path] = []
    for path in skill.rglob("*"):
        relative = PurePosixPath(path.relative_to(skill).as_posix())
        _validate_relative_path(relative)
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in release package: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"unsupported filesystem entry in release package: {relative}")
        if "__pycache__" in relative.parts or path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        _validate_release_file(path, skill)
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(skill).as_posix())


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
