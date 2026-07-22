# Changelog

All notable changes are documented here.

## [0.3.0] - 2026-07-22

### Added

- compact pre-generation visual direction for `create`, authorized `redesign`,
  and design-bearing `translate` work
- system-level reference interpretation, concrete generic AI-design default
  checks, and exactly one same-model critique and repair pass
- selectively loaded guidance for generated images, editorial/social graphics,
  and web/interface compositions
- weak-to-strong examples covering rule extraction, subject-specific structure,
  fixed information architecture, compact tool handoff, and flourish removal
- a separate six-case design-quality suite, original visual reference fixture,
  provenance schema, structural record grader, and external-client comparison
  protocol

### Changed

- expanded the skill from change-boundary safety to both boundary safety and
  positive design judgment without changing the eight-route contract
- consolidated the prior medium-neutral `frontend-design.md` guidance into
  `visual-direction.md` so shared rules are not duplicated across medium files
- updated runtime metadata, project validation, source audit, documentation,
  tests, and deterministic packaging for v0.3.0

### Compatibility

- preserves `meaningful_design_exists`, evidence priority, fixed/changeable
  dimensions, analysis-only mutation boundaries, and unauthorized-drift
  protection
- retains the v0.2.2 onboarding, installation and expectation guidance, and
  idempotent release-rerun behavior
- real ChatGPT- and Gemini-class before/after visual evaluations remain external
  client evidence and must not be inferred from structural graders

## [0.2.2] - 2026-07-22

### Added

- plain-language onboarding that explains what changes after installation and
  separates ChatGPT upload from Codex filesystem installation
- platform guidance, a copyable post-install verification prompt, an
  illustrative route decision, and answers to common first-user questions

### Changed

- made tagged Release workflow reruns replace existing ZIP and checksum assets
  instead of failing when the GitHub Release already exists

## [0.2.1] - 2026-07-20

### Added

- root `VERSION` as the single release-version source of truth
- provenance schema for v0.2.1+ semantic forward-test results, including
  execution, commit, model, suite, observed-route, and boundary-rationale fields

### Changed

- replaced the route contract's physical artifact flag with
  `meaningful_design_exists`
- allowed `create` contracts to preserve partial structural evidence such as a
  wireframe while establishing a new visual system
- required release tags and explicit package versions to match `VERSION`
- restricted runtime skill ZIP contents to documented files and directories,
  rejecting hidden, temporary, archive, symlink, credential-like, unexpected,
  and oversized entries
- made the semantic grader require provenance and per-case boundary rationales
  for new-schema results while retaining v0.2.0 records unchanged

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
