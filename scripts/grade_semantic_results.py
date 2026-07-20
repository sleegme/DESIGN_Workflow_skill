#!/usr/bin/env python3
"""Grade client-produced route decisions against the semantic smoke suite."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT / "evals/semantic-smoke.json"
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
SCHEMA_VERSION = "1.0"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")


def _required_string(result: dict[str, object], field: str) -> str:
    value = result.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"result.{field} must be a non-empty string")
    return value.strip()


def validate_provenance(result: dict[str, object]) -> bool:
    """Validate v0.2.1+ provenance; return False for preserved legacy records."""
    schema_version = result.get("schema_version")
    if schema_version is None:
        legacy_revision = result.get("skill_revision")
        if isinstance(legacy_revision, str) and legacy_revision.startswith("v0.2.0"):
            return False
        raise ValueError(
            "result.schema_version is required; only recorded v0.2.0 results use the legacy format"
        )
    if schema_version != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported result.schema_version {schema_version!r}; expected {SCHEMA_VERSION!r}"
        )

    executed_at = _required_string(result, "executed_at")
    try:
        timestamp = datetime.fromisoformat(executed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("result.executed_at must be an ISO 8601 timestamp") from exc
    if timestamp.tzinfo is None:
        raise ValueError("result.executed_at must include a timezone")

    commit_sha = _required_string(result, "commit_sha")
    if not COMMIT_RE.fullmatch(commit_sha):
        raise ValueError("result.commit_sha must be a 7-64 character hexadecimal commit SHA")
    skill_version = _required_string(result, "skill_version")
    if not SEMVER_RE.fullmatch(skill_version):
        raise ValueError("result.skill_version must be a semantic version")
    _required_string(result, "runner")
    _required_string(result, "model")
    _required_string(result, "reasoning_effort")
    _required_string(result, "suite_file")
    _required_string(result, "suite_revision")
    return True


def grade(suite: list[dict[str, object]], result: dict[str, object]) -> dict[str, object]:
    if not isinstance(result, dict):
        raise ValueError("result must be an object")
    has_provenance = validate_provenance(result)
    expected = {str(case["id"]): case for case in suite}
    raw_cases = result.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError("result.cases must be an array")
    if any(not isinstance(case, dict) for case in raw_cases):
        raise ValueError("every result case must be an object")
    case_ids = [str(case.get("id")) for case in raw_cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("result case ids must be unique")
    observed = {str(case.get("id")): case for case in raw_cases}
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise ValueError(f"result ids differ; missing={missing}, extra={extra}")

    details = []
    for case_id, expected_case in expected.items():
        item = observed[case_id]
        route = item.get("observed_route")
        boundary_preserved = item.get("boundary_preserved")
        if route not in ROUTES:
            raise ValueError(f"{case_id} has invalid observed_route: {route}")
        if not isinstance(boundary_preserved, bool):
            raise ValueError(f"{case_id} boundary_preserved must be boolean")
        boundary_rationale = item.get("boundary_rationale")
        if has_provenance and (
            not isinstance(boundary_rationale, str) or not boundary_rationale.strip()
        ):
            raise ValueError(f"{case_id} boundary_rationale must be a non-empty string")
        route_pass = route == expected_case["expected_route"]
        passed = route_pass and boundary_preserved
        details.append(
            {
                "id": case_id,
                "expected_route": expected_case["expected_route"],
                "observed_route": route,
                "expected_boundary": expected_case["expected_boundary"],
                "boundary_preserved": boundary_preserved,
                "boundary_rationale": boundary_rationale or item.get("notes", ""),
                "response_excerpt": item.get("response_excerpt", ""),
                "pass": passed,
                "notes": item.get("notes", ""),
            }
        )

    passed = sum(1 for item in details if item["pass"])
    graded = {
        "runner": result.get("runner", "unknown"),
        "summary": {"passed": passed, "total": len(details), "pass_rate": passed / len(details)},
        "requires_independent_boundary_review": True,
        "cases": details,
    }
    if has_provenance:
        for field in (
            "schema_version",
            "executed_at",
            "commit_sha",
            "skill_version",
            "client",
            "model",
            "reasoning_effort",
            "suite_file",
            "suite_revision",
        ):
            if field in result:
                graded[field] = result[field]
    else:
        graded["skill_revision"] = result.get("skill_revision", "unknown")
    return graded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", help="client-produced JSON result")
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="semantic suite JSON")
    parser.add_argument("--output", help="optional graded JSON output path")
    args = parser.parse_args()

    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    graded = grade(suite, result)
    rendered = json.dumps(graded, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if graded["summary"]["passed"] == graded["summary"]["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
