#!/usr/bin/env python3
"""Validate the repository and distributable design-workflow skill."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from scripts import grade_design_quality_results
    from scripts import grade_semantic_results
except ModuleNotFoundError:  # Direct execution puts scripts/ on sys.path.
    import grade_design_quality_results  # type: ignore[no-redef]
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
    "evals/design-quality-cases.json",
    "evals/design-quality-result.schema.json",
    "evals/fixtures/reference-system-study.svg",
    "scripts/grade_design_quality_results.py",
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
    "references/visual-direction.md",
    "references/generated-image-design.md",
    "references/editorial-social-design.md",
    "references/web-interface-design.md",
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


def require_graded_cases_match(
    graded_path: Path,
    graded: dict[str, object],
    computed: dict[str, object],
) -> None:
    """Compare a committed graded result to the grader's deterministic output.

    Provenance and execution fields (runner, commit id, timing, client identity)
    are pass-through echoes, not recomputed here, so they are never compared.
    The ``cases`` array is the deterministic derived layer: each committed case
    must have exactly the same deterministic field set as the recomputed case,
    and every deterministic value must agree.
    """
    require(isinstance(graded, dict), f"graded result is not an object: {graded_path.name}")
    require(
        graded.get("summary") == computed.get("summary"),
        f"graded summary is stale or inconsistent: {graded_path.name}",
    )
    graded_cases = graded.get("cases")
    computed_cases = computed.get("cases")
    require(isinstance(graded_cases, list), f"graded result missing cases array: {graded_path.name}")
    require(isinstance(computed_cases, list), "recomputed graded result missing cases array")
    require(len(graded_cases) == len(computed_cases), f"graded case count differs: {graded_path.name}")
    graded_ids = [str(case.get("id")) for case in graded_cases]
    computed_ids = [str(case.get("id")) for case in computed_cases]
    require(graded_ids == computed_ids, f"graded case ids/order differ: {graded_path.name}")
    graded_by_id = {str(case.get("id")): case for case in graded_cases}
    for case_id, computed_case in zip(computed_ids, computed_cases):
        committed = graded_by_id[case_id]
        committed_keys = set(committed.keys())
        computed_keys = set(computed_case.keys())
        missing = computed_keys - committed_keys
        extra = committed_keys - computed_keys
        require(not missing, f"{case_id} graded case missing deterministic fields {sorted(missing)}: {graded_path.name}")
        require(not extra, f"{case_id} graded case has unexpected fields {sorted(extra)}: {graded_path.name}")
        for field, computed_value in computed_case.items():
            require(
                committed[field] == computed_value,
                f"{case_id} graded case field {field!r} disagrees with recomputed grading: {graded_path.name}",
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
            f"{case['id']} meaningful_design_exists must be a bool",
        )
        require(
            isinstance(case["mutates_artifact"], bool),
            f"{case['id']} mutates_artifact must be a bool, got {type(case['mutates_artifact']).__name__}",
        )
        require(
            isinstance(case["redesign_authorized"], bool),
            f"{case['id']} redesign_authorized must be a bool, got {type(case['redesign_authorized']).__name__}",
        )
        counts[route] += 1
        mutating_routes = {"preserve", "expand", "create", "redesign", "translate"}
        non_mutating_routes = {"critique", "brand-check", "profile"}
        if route in mutating_routes:
            require(
                case["mutates_artifact"] is True,
                f"{case['id']} {route} route contract requires mutates_artifact: true",
            )
        elif route in non_mutating_routes:
            require(
                case["mutates_artifact"] is False,
                f"{case['id']} {route} route contract requires mutates_artifact: false",
            )
        if route == "redesign":
            require(
                case["redesign_authorized"] is True,
                f"{case['id']} {route} route contract requires redesign_authorized: true",
            )
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
        require_graded_cases_match(
            graded_path,
            graded,
            computed,
        )


def validate_design_quality_evidence() -> None:
    suite = json.loads((ROOT / "evals/design-quality-cases.json").read_text(encoding="utf-8"))
    require(isinstance(suite, list) and len(suite) >= 6, "need at least six design-quality cases")
    required_scenarios = {
        "image-no-reference",
        "image-with-reference",
        "poster-card-news",
        "redesign-fixed-dimensions",
        "web-interface",
        "realistic-image",
    }
    allowed_media = {"generated-image", "editorial-social", "web-interface"}
    allowed_observations = {
        "coherent_direction",
        "reference_rules_not_surface_copy",
        "generic_defaults_avoided_or_justified",
        "fixed_dimensions_preserved",
        "information_architecture_preserved",
        "bounded_critique_repair",
        "medium_constraints_applied",
        "realistic_specificity",
    }
    ids: set[str] = set()
    scenarios: set[str] = set()
    observations_seen: set[str] = set()
    for case in suite:
        required = {
            "id",
            "scenario",
            "medium",
            "prompt",
            "meaningful_design_exists",
            "expected_route",
            "redesign_authorized",
            "fixed",
            "required_observations",
        }
        require(required <= case.keys(), f"design-quality case missing fields: {case}")
        require(case["id"] not in ids, f"duplicate design-quality case id: {case['id']}")
        ids.add(case["id"])
        scenarios.add(case["scenario"])
        require(case["medium"] in allowed_media, f"unknown design-quality medium: {case['id']}")
        require(case["expected_route"] in ROUTES, f"unknown design-quality route: {case['id']}")
        require(
            isinstance(case["meaningful_design_exists"], bool),
            f"invalid design-quality meaningful_design_exists: {case['id']}",
        )
        require(
            isinstance(case["redesign_authorized"], bool),
            f"invalid design-quality redesign authorization: {case['id']}",
        )
        if case["expected_route"] == "create":
            require(
                case["meaningful_design_exists"] is False,
                f"design-quality create case has a meaningful design: {case['id']}",
            )
        if case["expected_route"] == "redesign":
            require(
                case["meaningful_design_exists"] is True,
                f"design-quality redesign case lacks a meaningful design: {case['id']}",
            )
            require(
                case["redesign_authorized"] is True,
                f"design-quality redesign case lacks authorization: {case['id']}",
            )
        else:
            require(
                case["redesign_authorized"] is False,
                f"non-redesign design-quality case authorizes redesign: {case['id']}",
            )
        required_observations = case["required_observations"]
        require(
            isinstance(required_observations, list) and required_observations,
            f"design-quality observations must be a non-empty array: {case['id']}",
        )
        require(
            len(required_observations) == len(set(required_observations)),
            f"duplicate design-quality observation: {case['id']}",
        )
        require(
            set(required_observations) <= allowed_observations,
            f"unknown design-quality observation: {case['id']}",
        )
        observations_seen.update(required_observations)
        if "reference_fixture" in case:
            require(
                (ROOT / case["reference_fixture"]).is_file(),
                f"missing design-quality reference fixture: {case['reference_fixture']}",
            )

    require(scenarios == required_scenarios, f"design-quality scenario coverage differs: {scenarios}")
    require(
        observations_seen == allowed_observations,
        f"design-quality observable coverage differs: {observations_seen}",
    )

    raw_paths = sorted((ROOT / "evals/results").glob("*-design-quality.raw.json"))
    for raw_path in raw_paths:
        graded_path = raw_path.with_name(raw_path.name.replace(".raw.json", ".json"))
        require(graded_path.exists(), f"missing graded design-quality result for {raw_path.name}")
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        graded = json.loads(graded_path.read_text(encoding="utf-8"))
        computed = grade_design_quality_results.grade(suite, raw)
        require_graded_cases_match(
            graded_path,
            graded,
            computed,
        )
        require(
            graded.get("requires_independent_visual_review") is True
            and graded.get("supports_universal_aesthetic_claim") is False,
            f"design-quality result overstates structural evidence: {graded_path.name}",
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
        design_quality_schema = json.loads(
            (ROOT / "evals/design-quality-result.schema.json").read_text(encoding="utf-8")
        )
        require(
            design_quality_schema.get("properties", {}).get("schema_version", {}).get("const")
            == grade_design_quality_results.SCHEMA_VERSION,
            "design-quality result schema version disagrees with the grader",
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

        for adapted in ("references/visual-direction.md", "references/design-profile.md"):
            text = (SKILL / adapted).read_text(encoding="utf-8")
            require("Source and modification notice" in text, f"missing source notice: {adapted}")

        json.loads((SKILL / "assets/route-contract.example.json").read_text(encoding="utf-8"))
        validate_links()
        validate_route_cases()
        validate_trigger_cases()
        validate_semantic_evidence()
        validate_design_quality_evidence()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: project structure, skill boundary, links, legal files, and eval fixtures are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
