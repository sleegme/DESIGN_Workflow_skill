#!/usr/bin/env python3
"""Validate the repository and distributable design-workflow skill."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from scripts import grade_semantic_results
except ModuleNotFoundError:  # Direct execution puts scripts/ on sys.path.
    import grade_semantic_results  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "design-workflow"
ROUTES = {
    "preserve",
    "expand",
    "create",
    "redesign",
    "critique",
    "brand-check",
    "translate",
    "profile",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")

REQUIRED_PROJECT_FILES = {
    "README.md",
    "README.ko.md",
    "LICENSE",
    "NOTICE",
    "SOURCE_AUDIT.md",
    "THIRD_PARTY_NOTICES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "VERSION",
    "requirements-dev.txt",
    ".gitattributes",
    ".gitignore",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    "evals/README.md",
    "evals/routing-cases.json",
    "evals/trigger-cases.json",
    "evals/semantic-smoke.json",
    "evals/semantic-result.schema.json",
    "scripts/grade_semantic_results.py",
    "scripts/package_project.py",
    "scripts/package_skill.py",
}
REQUIRED_SKILL_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "references/routing.md",
    "references/evidence-security.md",
    "references/preservation.md",
    "references/frontend-design.md",
    "references/critique.md",
    "references/media-translation.md",
    "references/design-profile.md",
    "assets/DESIGN.template.md",
    "assets/PROFILE.template.md",
    "assets/route-contract.example.json",
    "scripts/validate_route_contract.py",
}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    require(end >= 0, "SKILL.md frontmatter is not closed")
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        require(":" in line, f"unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"\'')
    return metadata, text[end + 5 :]


def validate_links() -> None:
    for path in SKILL.rglob("*.md"):
        for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if clean:
                require(
                    (path.parent / clean).resolve().exists(),
                    f"broken link in {path.relative_to(ROOT)}: {target}",
                )


def validate_route_cases() -> None:
    cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
    require(isinstance(cases, list) and len(cases) >= 40, "need at least 40 route cases")
    ids: set[str] = set()
    counts: Counter[str] = Counter()
    for case in cases:
        required = {
            "id",
            "prompt",
            "meaningful_design_exists",
            "expected_route",
            "mutates_artifact",
            "redesign_authorized",
            "basis",
        }
        require(required <= case.keys(), f"route case missing fields: {case}")
        require(case["id"] not in ids, f"duplicate route case id: {case['id']}")
        ids.add(case["id"])
        route = case["expected_route"]
        require(route in ROUTES, f"unknown route in {case['id']}: {route}")
        require(
            isinstance(case["meaningful_design_exists"], bool),
            f"invalid meaningful_design_exists in {case['id']}",
        )
        counts[route] += 1
        if route == "redesign":
            require(case["redesign_authorized"] is True, f"{case['id']} lacks redesign authorization")
        if route == "create":
            require(
                case["meaningful_design_exists"] is False,
                f"{case['id']} create case has a meaningful existing design",
            )
        if route in {"preserve", "expand", "redesign"}:
            require(
                case["meaningful_design_exists"] is True,
                f"{case['id']} requires a meaningful existing design",
            )
        if route in {"critique", "brand-check", "profile"}:
            require(case["mutates_artifact"] is False, f"{case['id']} must not mutate design")
    require(all(counts[route] >= 5 for route in ROUTES), f"insufficient route coverage: {counts}")


def validate_trigger_cases() -> None:
    cases = json.loads((ROOT / "evals/trigger-cases.json").read_text(encoding="utf-8"))
    require(isinstance(cases, list) and len(cases) >= 24, "need at least 24 trigger cases")
    queries: set[str] = set()
    counts = Counter()
    for case in cases:
        require(
            {"id", "query", "should_trigger", "category", "rationale"} <= case.keys(),
            f"trigger case missing fields: {case}",
        )
        require(case["query"] not in queries, f"duplicate trigger query: {case['query']}")
        queries.add(case["query"])
        require(isinstance(case["should_trigger"], bool), f"invalid trigger label: {case['id']}")
        counts[case["should_trigger"]] += 1
    require(counts[True] >= 12 and counts[False] >= 12, f"unbalanced trigger coverage: {counts}")


def validate_semantic_evidence() -> None:
    suite = json.loads((ROOT / "evals/semantic-smoke.json").read_text(encoding="utf-8"))
    require(isinstance(suite, list) and suite, "semantic smoke suite must be a non-empty array")
    for case in suite:
        require(
            {"id", "prompt", "meaningful_design_exists", "expected_route", "expected_boundary"}
            <= case.keys(),
            f"semantic case missing fields: {case}",
        )
        require(case["expected_route"] in ROUTES, f"unknown semantic route: {case['id']}")
        require(
            isinstance(case["meaningful_design_exists"], bool),
            f"invalid semantic meaningful_design_exists: {case['id']}",
        )
        if case["expected_route"] == "create":
            require(
                case["meaningful_design_exists"] is False,
                f"semantic create case has a meaningful design: {case['id']}",
            )

    partial_create = next((case for case in suite if case["id"] == "S06"), None)
    require(partial_create is not None, "semantic smoke suite is missing S06")
    require(
        partial_create.get("fixed") == ["content order", "information architecture"],
        "S06 must preserve its partial structural evidence",
    )
    require(
        set(partial_create.get("changeable", []))
        == {"visual language", "typography", "palette", "component styling"},
        "S06 must leave visual design dimensions changeable",
    )

    expected = {case["id"]: case["expected_route"] for case in suite}
    raw_paths = sorted((ROOT / "evals/results").glob("*-forward-test.raw.json"))
    require(raw_paths, "no recorded semantic forward-test results")
    for raw_path in raw_paths:
        graded_path = raw_path.with_name(raw_path.name.replace(".raw.json", ".json"))
        require(graded_path.exists(), f"missing graded semantic result for {raw_path.name}")
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        graded = json.loads(graded_path.read_text(encoding="utf-8"))
        if "schema_version" in raw:
            require(
                raw_path.name.startswith(f"v{raw.get('skill_version')}-"),
                f"semantic result filename disagrees with skill_version: {raw_path.name}",
            )
        observed = {case["id"]: case for case in raw["cases"]}
        require(
            set(observed) == set(expected),
            f"semantic forward-test ids do not match the smoke suite: {raw_path.name}",
        )
        computed = grade_semantic_results.grade(suite, raw)
        require(
            graded.get("summary") == computed["summary"],
            f"graded semantic summary is stale or inconsistent: {graded_path.name}",
        )


def main() -> int:
    try:
        require(SKILL.is_dir(), "missing design-workflow skill directory")
        missing_project = sorted(path for path in REQUIRED_PROJECT_FILES if not (ROOT / path).exists())
        require(not missing_project, f"missing project files: {', '.join(missing_project)}")
        missing_skill = sorted(path for path in REQUIRED_SKILL_FILES if not (SKILL / path).exists())
        require(not missing_skill, f"missing skill files: {', '.join(missing_skill)}")

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        require(VERSION_RE.fullmatch(version) is not None, f"invalid VERSION: {version!r}")

        semantic_schema = json.loads(
            (ROOT / "evals/semantic-result.schema.json").read_text(encoding="utf-8")
        )
        require(
            semantic_schema.get("properties", {}).get("schema_version", {}).get("const")
            == grade_semantic_results.SCHEMA_VERSION,
            "semantic result schema version disagrees with the grader",
        )

        skill_files = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("SKILL.md")]
        require(skill_files == ["design-workflow/SKILL.md"], f"expected one distributable SKILL.md: {skill_files}")

        metadata, body = parse_frontmatter(SKILL / "SKILL.md")
        require(set(metadata) == {"name", "description"}, "SKILL.md frontmatter must contain only name and description")
        name = metadata["name"]
        description = metadata["description"]
        require(NAME_RE.fullmatch(name) is not None and len(name) <= 64, f"invalid skill name: {name}")
        require(name == SKILL.name, "skill name must match its parent directory")
        require(1 <= len(description) <= 1024, "description must contain 1-1024 characters")
        require(body.strip(), "SKILL.md body must not be empty")
        require(body.count("\n") < 500, "SKILL.md body must stay under 500 lines")

        forbidden = {"README.md", "README.ko.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md"}
        present_forbidden = sorted(path for path in forbidden if (SKILL / path).exists())
        require(not present_forbidden, f"human project docs leaked into skill: {present_forbidden}")

        openai_yaml = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        for expected in ("display_name:", "short_description:", "default_prompt:", "$design-workflow"):
            require(expected in openai_yaml, f"agents/openai.yaml missing {expected}")

        for adapted in ("references/frontend-design.md", "references/design-profile.md"):
            text = (SKILL / adapted).read_text(encoding="utf-8")
            require("Source and modification notice" in text, f"missing source notice: {adapted}")

        json.loads((SKILL / "assets/route-contract.example.json").read_text(encoding="utf-8"))
        validate_links()
        validate_route_cases()
        validate_trigger_cases()
        validate_semantic_evidence()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: project structure, skill boundary, links, legal files, and eval fixtures are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
