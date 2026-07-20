# Evaluation protocol

The evaluation layers answer different questions and must not be presented as
interchangeable evidence.

- Deterministic unit and invariant validation checks repository structure,
  route-contract rules, fixture consistency, packaging boundaries, and archive
  reproducibility. It does not run a model.
- Activation tests use `trigger-cases.json` to measure whether a particular
  client and model load the skill. Their results are client- and model-dependent.
- Semantic forward tests load the skill, run `semantic-smoke.json`, and record
  the route actually observed. They test post-activation behavior for one
  recorded environment, not universal routing accuracy.
- Boundary judgments remain semantic claims. The grader verifies that a result
  includes a boolean decision and a rationale, but an independent person or
  model must review the response evidence against `expected_boundary`.

## Forward-test result format

Results produced for skill version 0.2.1 or later use
`semantic-result.schema.json` and `schema_version: "1.0"`. Record:

- `executed_at`: timezone-qualified ISO 8601 execution time
- `commit_sha`: exact repository commit tested
- `skill_version`: value from `VERSION`
- `client` when applicable and `runner`: the execution client/runner identity
- `model` and `reasoning_effort`: the actual runtime configuration
- `suite_file` and `suite_revision`: suite path and immutable revision or blob
  identifier
- one entry per suite case with `observed_route`, `boundary_preserved`, and a
  concise `boundary_rationale`
- optionally, `response_excerpt` or `notes` for independent review, subject to
  privacy and copyright constraints

Name recorded raw files `v<skill_version>-<runner>-forward-test.raw.json`; the
project validator checks that new-schema filenames and `skill_version` agree.

Grade a completed raw result with:

```bash
python scripts/grade_semantic_results.py path/to/result.raw.json \
  --output path/to/result.json
```

The grader checks provenance shape, route equality, declared boundary status,
and rationale presence. It deliberately reports
`requires_independent_boundary_review: true`; it does not infer semantic
boundary preservation from the rationale or response.

Files under `results/` from v0.2.0 predate schema 1.0 and are retained without
inventing missing timestamps, commit SHAs, model names, or reasoning settings.
