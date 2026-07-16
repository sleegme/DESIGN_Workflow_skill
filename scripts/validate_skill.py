#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BANNED_CONTEXT = (
    "ModuleScale",
    "modulescale",
    "Liquid Start",
    "liquid-start",
    "Midnight Teal",
)
REQUIRED = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_AUDIT.md",
    "CHANGELOG.md",
    "RELEASE_CHECKLIST.md",
    "tests/routing-cases.json",
    "tests/trigger-cases.json",
    ".github/workflows/ci.yml",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        fail("SKILL.md must begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail("SKILL.md frontmatter is not closed")
    data: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(0, data)]
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            fail(f"unsupported frontmatter line: {raw}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value == "":
            child: dict[str, object] = {}
            current[key] = child
            stack.append((indent + 2, child))
        else:
            current[key] = value.strip('"\'')
    return data


def validate_links(root: Path) -> None:
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                fail(f"broken relative link in {path.relative_to(root)}: {target}")


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    for rel in REQUIRED:
        if not (root / rel).exists():
            fail(f"missing required path: {rel}")

    skill_files = list(root.rglob("SKILL.md"))
    if skill_files != [root / "SKILL.md"]:
        fail("the distributable package must contain exactly one SKILL.md")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    meta = parse_frontmatter(skill_text)

    name = str(meta.get("name", ""))
    description = str(meta.get("description", ""))
    license_name = str(meta.get("license", ""))

    if not NAME_RE.fullmatch(name):
        fail(f"invalid skill name: {name!r}")
    if root.name != name:
        fail(f"directory name {root.name!r} must match skill name {name!r}")
    if not 1 <= len(description) <= 1024:
        fail("description must contain 1-1024 characters")
    if license_name != "Apache-2.0":
        fail("license frontmatter must be Apache-2.0")
    if skill_text.count("\n") + 1 > 500:
        fail("SKILL.md exceeds 500 lines")

    metadata = meta.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("version") != "0.1.0":
        fail("metadata.version must be 0.1.0")

    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".json", ".yml", ".yaml", ""}
    )
    for banned in BANNED_CONTEXT:
        if banned in combined:
            fail(f"project-specific context found: {banned}")

    for adapted in (
        root / "references/frontend-design.md",
        root / "references/design-profile.md",
    ):
        text = adapted.read_text(encoding="utf-8")
        if "Source and modification notice" not in text:
            fail(f"missing prominent modification notice: {adapted.relative_to(root)}")

    audit = (root / "SOURCE_AUDIT.md").read_text(encoding="utf-8")
    notices = (root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for required_name in ("Anthropic", "Google", "Apache-2.0"):
        if required_name not in audit + notices:
            fail(f"source audit is missing {required_name}")
    if "No traceable Canva" not in audit:
        fail("audit must explicitly record that unverified Canva material is excluded")

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [0.1.0]" not in changelog:
        fail("CHANGELOG.md is missing v0.1.0")

    validate_links(root)

    print("PASS: Agent Skill structure, metadata, links, provenance, and release files are valid.")


if __name__ == "__main__":
    main()
