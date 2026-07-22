#!/usr/bin/env python3
"""Validate and summarize declared design-quality evaluation observations.

This grader checks provenance, case coverage, and evidence-record structure. It
does not inspect artifacts or prove aesthetic improvement.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT / "evals/design-quality-cases.json"
SCHEMA_VERSION = "1.0"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
RESULTS = {"pass", "fail"}


def _required_string(record: dict[str, object], field: str, prefix: str = "result") -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{prefix}.{field} must be a non-empty string")
    return value.strip()


def validate_provenance(result: dict[str, object]) -> None:
    if result.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"result.schema_version must be {SCHEMA_VERSION!r}"
        )
    executed_at = _required_string(result, "executed_at")
    try:
        timestamp = datetime.fromisoformat(executed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("result.executed_at must be an ISO 8601 timestamp") from exc
    if timestamp.tzinfo is None:
        raise ValueError("result.executed_at must include a timezone")

    if not COMMIT_RE.fullmatch(_required_string(result, "commit_sha")):
        raise ValueError("result.commit_sha must be a 7-64 character hexadecimal commit SHA")
    if not SEMVER_RE.fullmatch(_required_string(result, "skill_version")):
        raise ValueError("result.skill_version must be a semantic version")
    for field in (
        "client",
        "runner",
        "model",
        "reasoning_effort",
        "suite_file",
        "suite_revision",
        "evaluator",
    ):
        _required_string(result, field)
    if result["suite_file"] != "evals/design-quality-cases.json":
        raise ValueError("result.suite_file must identify the design-quality suite")


def grade(suite: list[dict[str, object]], result: dict[str, object]) -> dict[str, object]:
    if not isinstance(result, dict):
        raise ValueError("result must be an object")
    validate_provenance(result)
    expected = {str(case["id"]): case for case in suite}
    raw_cases = result.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("result.cases must be a non-empty array")
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

    details: list[dict[str, object]] = []
    for case_id, expected_case in expected.items():
        item = observed[case_id]
        baseline_artifact = _required_string(item, "baseline_artifact", case_id)
        candidate_artifact = _required_string(item, "candidate_artifact", case_id)
        if baseline_artifact == candidate_artifact:
            raise ValueError(f"{case_id} baseline and candidate artifacts must differ")
        raw_observations = item.get("observations")
        if not isinstance(raw_observations, list) or not raw_observations:
            raise ValueError(f"{case_id}.observations must be a non-empty array")
        if any(not isinstance(observation, dict) for observation in raw_observations):
            raise ValueError(f"{case_id}.observations must contain objects")
        properties = [str(observation.get("property")) for observation in raw_observations]
        if len(properties) != len(set(properties)):
            raise ValueError(f"{case_id}.observations contains duplicate properties")
        expected_properties = set(expected_case["required_observations"])
        if set(properties) != expected_properties:
            missing = sorted(expected_properties - set(properties))
            extra = sorted(set(properties) - expected_properties)
            raise ValueError(
                f"{case_id} observation properties differ; missing={missing}, extra={extra}"
            )
        normalized = []
        for observation in raw_observations:
            property_name = str(observation["property"])
            decision = observation.get("result")
            if decision not in RESULTS:
                raise ValueError(f"{case_id}.{property_name}.result must be pass or fail")
            evidence = _required_string(
                observation, "evidence", f"{case_id}.{property_name}"
            )
            normalized.append(
                {"property": property_name, "result": decision, "evidence": evidence}
            )
        details.append(
            {
                "id": case_id,
                "baseline_artifact": baseline_artifact,
                "candidate_artifact": candidate_artifact,
                "declared_pass": all(item["result"] == "pass" for item in normalized),
                "observations": normalized,
            }
        )

    passed = sum(1 for item in details if item["declared_pass"])
    return {
        **{field: result[field] for field in (
            "schema_version",
            "executed_at",
            "commit_sha",
            "skill_version",
            "client",
            "runner",
            "model",
            "reasoning_effort",
            "suite_file",
            "suite_revision",
            "evaluator",
        )},
        "summary": {
            "declared_passed": passed,
            "total": len(details),
            "declared_pass_rate": passed / len(details),
        },
        "result_type": "structural_record_check",
        "requires_independent_visual_review": True,
        "supports_universal_aesthetic_claim": False,
        "cases": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", help="client-produced design-quality result JSON")
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="design-quality suite JSON")
    parser.add_argument("--output", help="optional graded JSON output path")
    args = parser.parse_args()

    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    graded = grade(suite, result)
    rendered = json.dumps(graded, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if graded["summary"]["declared_passed"] == graded["summary"]["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
