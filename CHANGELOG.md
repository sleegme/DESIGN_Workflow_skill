# Changelog

All notable changes are documented here.

## [0.2.0] - 2026-07-17

### Added

- installable `design-workflow/` package whose directory matches the skill name
- generated `agents/openai.yaml` interface metadata
- mixed-route, partial-evidence, and instruction-security guidance
- dependency-free route-contract validator and example contract
- balanced trigger cases and a client-gradeable semantic smoke suite
- recorded independent 16-case forward test covering all eight routes
- project validator, unit tests, deterministic skill/project ZIP packaging, and SHA-256 output
- CI with official `agentskills` validation and tagged GitHub Release automation

### Changed

- clarified `expand` versus `translate` and dimension-specific preservation
- narrowed activation to tasks that require visual design judgment
- separated human repository documentation and evals from the runtime skill
- replaced committed self-reported dry-run results with a reproducible grading
  protocol

### Removed

- root-level `SKILL.md` layout that produced an invalid default installation name
- unrelated runtime traceback from the old routing report
- CI claims that fixture consistency was semantic model validation

## [0.1.0] - 2026-07-16

- initial medium-neutral routing skill with eight routes
- preservation-versus-redesign boundary, references, templates, and provenance
