from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "design-workflow/scripts/validate_route_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_route_contract", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RouteContractTests(unittest.TestCase):
    def contract(self, route: str) -> dict[str, object]:
        scopes = {
            "preserve": "local",
            "expand": "system",
            "create": "system",
            "redesign": "replacement",
            "critique": "none",
            "brand-check": "none",
            "translate": "system",
            "profile": "documentation",
        }
        return {
            "primary_route": route,
            "secondary_routes": [],
            "artifact_exists": route != "create",
            "redesign_authorized": route == "redesign",
            "governing_evidence": ["user request"],
            "fixed": ["content hierarchy"],
            "changeable": ["requested surface"],
            "unknowns": [],
            "mutation_scope": scopes[route],
        }

    def test_all_routes_accept_valid_contracts(self) -> None:
        for route in sorted(MODULE.ROUTES):
            with self.subTest(route=route):
                self.assertEqual(MODULE.validate_contract(self.contract(route)), [])

    def test_redesign_requires_explicit_authorization(self) -> None:
        contract = self.contract("redesign")
        contract["redesign_authorized"] = False
        self.assertIn("redesign requires redesign_authorized=true", MODULE.validate_contract(contract))

    def test_create_rejects_existing_artifact(self) -> None:
        contract = self.contract("create")
        contract["artifact_exists"] = True
        self.assertIn("create requires artifact_exists=false", MODULE.validate_contract(contract))

    def test_analysis_rejects_mutation(self) -> None:
        contract = self.contract("critique")
        contract["mutation_scope"] = "local"
        self.assertIn("critique requires mutation_scope=none", MODULE.validate_contract(contract))

    def test_fixed_and_changeable_must_not_overlap(self) -> None:
        contract = self.contract("preserve")
        contract["changeable"] = ["content hierarchy"]
        errors = MODULE.validate_contract(contract)
        self.assertTrue(any(error.startswith("fixed and changeable overlap") for error in errors))

    def test_secondary_routes_are_unique_and_distinct(self) -> None:
        contract = self.contract("preserve")
        contract["secondary_routes"] = ["preserve", "critique", "critique"]
        errors = MODULE.validate_contract(contract)
        self.assertIn("primary_route must not also appear in secondary_routes", errors)
        self.assertIn("secondary_routes must not contain duplicates", errors)


if __name__ == "__main__":
    unittest.main()
