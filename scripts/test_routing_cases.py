#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_ROUTES = {
    "preserve",
    "expand",
    "create",
    "redesign",
    "critique",
    "brand-check",
    "translate",
    "profile",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    cases = json.loads((ROOT / "tests/routing-cases.json").read_text(encoding="utf-8"))
    results = json.loads(
        (ROOT / "tests/results/v0.1.0-authoring-dry-run.json").read_text(encoding="utf-8")
    )

    if len(cases) < 32:
        fail("routing suite must contain at least 32 realistic cases")

    counts = Counter()
    ids = set()
    by_id = {}
    for case in cases:
        case_id = case["id"]
        if case_id in ids:
            fail(f"duplicate case id: {case_id}")
        ids.add(case_id)
        route = case["expected_route"]
        if route not in VALID_ROUTES:
            fail(f"unknown route {route!r} in {case_id}")
        counts[route] += 1
        by_id[case_id] = case

        if route == "redesign" and not case["redesign_authorized"]:
            fail(f"{case_id}: redesign must be explicitly authorized")
        if route in {"preserve", "expand", "translate"} and case["redesign_authorized"]:
            fail(f"{case_id}: non-redesign route cannot carry redesign authorization")
        if route in {"critique", "brand-check", "profile"} and case["mutates_artifact"]:
            fail(f"{case_id}: analysis/profile route must not mutate the design artifact")
        if route == "create" and case["artifact"]:
            fail(f"{case_id}: create cases must not have a meaningful existing artifact")
        if route in {"preserve", "expand", "redesign", "critique", "brand-check",
                     "translate", "profile"} and not case["artifact"]:
            fail(f"{case_id}: route requires an existing artifact/evidence")

    missing = [route for route in VALID_ROUTES if counts[route] < 4]
    if missing:
        fail(f"each route needs at least four cases; missing coverage: {missing}")

    observed = {item["id"]: item for item in results["cases"]}
    if set(observed) != ids:
        fail("dry-run result ids do not match routing cases")

    failures = []
    for case_id, case in by_id.items():
        item = observed[case_id]
        if item["observed_route"] != case["expected_route"] or not item["pass"]:
            failures.append(case_id)
    if failures:
        fail(f"authoring dry run failed: {failures}")

    trigger_cases = json.loads(
        (ROOT / "tests/trigger-cases.json").read_text(encoding="utf-8")
    )
    positives = sum(1 for case in trigger_cases if case["should_trigger"])
    negatives = len(trigger_cases) - positives
    if positives < 8 or negatives < 8:
        fail("trigger suite needs at least 8 positive and 8 negative cases")

    print(
        f"PASS: {len(cases)} routing cases across {len(VALID_ROUTES)} routes; "
        f"{positives} trigger and {negatives} near-miss cases; authoring dry run passed."
    )


if __name__ == "__main__":
    main()
