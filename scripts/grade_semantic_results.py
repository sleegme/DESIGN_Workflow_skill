#!/usr/bin/env python3
"""Grade client-produced route decisions against the semantic smoke suite."""

from __future__ import annotations

import argparse
import json
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


def grade(suite: list[dict[str, object]], result: dict[str, object]) -> dict[str, object]:
    expected = {str(case["id"]): case for case in suite}
    raw_cases = result.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError("result.cases must be an array")
    observed = {str(case.get("id")): case for case in raw_cases if isinstance(case, dict)}
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
        route_pass = route == expected_case["expected_route"]
        passed = route_pass and boundary_preserved
        details.append(
            {
                "id": case_id,
                "expected_route": expected_case["expected_route"],
                "observed_route": route,
                "boundary_preserved": boundary_preserved,
                "pass": passed,
                "notes": item.get("notes", ""),
            }
        )

    passed = sum(1 for item in details if item["pass"])
    return {
        "runner": result.get("runner", "unknown"),
        "skill_revision": result.get("skill_revision", "unknown"),
        "summary": {"passed": passed, "total": len(details), "pass_rate": passed / len(details)},
        "cases": details,
    }


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
