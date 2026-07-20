#!/usr/bin/env python3
"""Validate a design-workflow route contract.

The script uses only the Python standard library so a skill consumer can run it
without installing project dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

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
MUTATION_SCOPES = {"none", "local", "system", "replacement", "documentation"}
REQUIRED_FIELDS = {
    "primary_route",
    "secondary_routes",
    "meaningful_design_exists",
    "redesign_authorized",
    "governing_evidence",
    "fixed",
    "changeable",
    "unknowns",
    "mutation_scope",
}


def _string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array of strings")
        return []
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{field} must contain only non-empty strings")
        return []
    return [item.strip() for item in value]


def validate_contract(contract: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["contract must be a JSON object"]

    missing = sorted(REQUIRED_FIELDS - contract.keys())
    extra = sorted(contract.keys() - REQUIRED_FIELDS)
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown fields: {', '.join(extra)}")
    if missing:
        return errors

    primary = contract["primary_route"]
    if primary not in ROUTES:
        errors.append(f"primary_route must be one of: {', '.join(sorted(ROUTES))}")

    secondary = _string_list(contract["secondary_routes"], "secondary_routes", errors)
    invalid_secondary = sorted(set(secondary) - ROUTES)
    if invalid_secondary:
        errors.append(f"unknown secondary routes: {', '.join(invalid_secondary)}")
    if primary in secondary:
        errors.append("primary_route must not also appear in secondary_routes")
    if len(secondary) != len(set(secondary)):
        errors.append("secondary_routes must not contain duplicates")

    meaningful_design_exists = contract["meaningful_design_exists"]
    redesign_authorized = contract["redesign_authorized"]
    if not isinstance(meaningful_design_exists, bool):
        errors.append("meaningful_design_exists must be a boolean")
    if not isinstance(redesign_authorized, bool):
        errors.append("redesign_authorized must be a boolean")

    evidence = _string_list(contract["governing_evidence"], "governing_evidence", errors)
    fixed = _string_list(contract["fixed"], "fixed", errors)
    changeable = _string_list(contract["changeable"], "changeable", errors)
    _string_list(contract["unknowns"], "unknowns", errors)

    if not evidence:
        errors.append("governing_evidence must contain at least one source")
    overlap = sorted(set(fixed) & set(changeable))
    if overlap:
        errors.append(f"fixed and changeable overlap: {', '.join(overlap)}")

    scope = contract["mutation_scope"]
    if scope not in MUTATION_SCOPES:
        errors.append(
            f"mutation_scope must be one of: {', '.join(sorted(MUTATION_SCOPES))}"
        )

    selected_routes = {primary, *secondary}
    if "redesign" in selected_routes and redesign_authorized is not True:
        errors.append("redesign requires redesign_authorized=true")
    if primary == "create" and meaningful_design_exists is not False:
        errors.append("create requires meaningful_design_exists=false")
    if primary in {"preserve", "expand", "redesign"} and meaningful_design_exists is not True:
        errors.append(f"{primary} requires meaningful_design_exists=true")

    expected_scopes = {
        "preserve": {"local"},
        "expand": {"system"},
        "create": {"system"},
        "redesign": {"replacement"},
        "critique": {"none"},
        "brand-check": {"none"},
        "translate": {"system"},
        "profile": {"documentation"},
    }
    if primary in expected_scopes and scope not in expected_scopes[primary]:
        allowed = ", ".join(sorted(expected_scopes[primary]))
        errors.append(f"{primary} requires mutation_scope={allowed}")

    return errors


def _read_contract(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", help="JSON contract path, or - for stdin")
    args = parser.parse_args()

    try:
        contract = _read_contract(args.contract)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2

    errors = validate_contract(contract)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
