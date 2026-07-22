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
- Design-quality evaluations use `design-quality-cases.json` as a separate layer.
  They compare a no-skill baseline with a skill-enabled candidate and record
  observable direction, reference interpretation, default avoidance, boundary,
  critique-repair, and medium-specific evidence. Structural grading validates
  the record; independent artifact review judges the evidence.
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

## Design-quality comparison protocol

Run all cases in `design-quality-cases.json` twice in the same client and model:

1. **Baseline:** disable or omit `design-workflow`; keep the prompt, attached
   fixture, model, settings, and tool constant.
2. **Candidate:** load the packaged v0.3.0 skill and repeat the same task once.
3. Save stable local paths, hashes, or client artifact identifiers for both
   outputs. Do not use a prose description in place of an unavailable artifact.
4. Have an independent reviewer inspect both outputs and record every required
   property as `pass` or `fail` with concrete evidence. For
   `bounded_critique_repair`, identify the draft defect, the actual repaired
   result, and that no second critique pass occurred—not merely a stated
   intention to critique.
5. Grade the completed record:

```bash
python scripts/grade_design_quality_results.py \
  evals/results/v0.3.0-<client>-design-quality.raw.json \
  --output evals/results/v0.3.0-<client>-design-quality.json
```

Use `design-quality-result.schema.json`. Record client and model provenance,
including reasoning settings, exact commit, suite revision, and evaluator.
Attach `evals/fixtures/reference-system-study.svg` for DQ02. Preserve generated
artifacts outside the runtime skill ZIP; if they cannot be published, retain
reviewable hashes or access-controlled identifiers without disclosing private
content.

The design-quality grader confirms complete case coverage, exact observable
coverage, non-empty evidence, and declared pass/fail results. Its output always
states `result_type: structural_record_check`,
`requires_independent_visual_review: true`, and
`supports_universal_aesthetic_claim: false`. It cannot prove that an artifact is
beautiful, that a repair happened, or that the skill universally improves every
model or generator.

At least one ChatGPT-class baseline/candidate run is required before final
release acceptance. Run the same comparison in a Gemini-class client when one
is available. When those clients are unavailable, leave the criteria explicitly
pending; never create synthetic result records or relabel a run from another
client.
