# design-workflow

**English** | [한국어](README.ko.md)

`design-workflow` is an Agent Skill that routes visual work by intent and
prevents accidental redesigns. It acts as a policy layer before a specialized
document, slide, image, design, browser, or code workflow performs the edit.

The invariant is simple: preserve a meaningful existing design unless the user
clearly authorizes replacement.

## Routes

| Route | Purpose |
|---|---|
| `preserve` | Correct or polish an existing artifact locally |
| `expand` | Add a sibling part that inherits an existing system |
| `create` | Establish a direction when no meaningful design exists |
| `redesign` | Replace explicitly authorized design dimensions |
| `critique` | Analyze without editing |
| `brand-check` | Audit against brand or system evidence |
| `translate` | Recompose a source for a new medium or constraint |
| `profile` | Derive `DESIGN.md` or `.design/PROFILE.md` from evidence |

## Repository layout

```text
design-workflow-project/
├── design-workflow/             # the distributable Agent Skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   ├── assets/
│   ├── scripts/
│   ├── LICENSE
│   ├── NOTICE
│   └── THIRD_PARTY_NOTICES.md
├── evals/                       # route, trigger, and semantic smoke cases
├── VERSION                      # single release-version source of truth
├── scripts/                     # project validation, grading, and packaging
├── tests/                       # dependency-free unit tests
└── .github/workflows/           # CI and tagged release automation
```

Keeping the skill in a literal `design-workflow/` directory makes the package
conform to the Agent Skills requirement that the parent directory match the
frontmatter `name`.

## Installation

Install only the nested `design-workflow/` directory into the skills directory
used by your client.

```bash
git clone https://github.com/sleegme/DESIGN_Workflow_skill.git
cp -R DESIGN_Workflow_skill/design-workflow ~/.codex/skills/design-workflow
```

PowerShell:

```powershell
git clone https://github.com/sleegme/DESIGN_Workflow_skill.git
Copy-Item -Recurse DESIGN_Workflow_skill\design-workflow $env:USERPROFILE\.codex\skills\design-workflow
```

A tagged GitHub Release contains `design-workflow-<version>.zip`. The archive
always expands to a top-level `design-workflow/` directory and includes a SHA-256
checksum.

## Usage

Invoke the skill explicitly or let a compatible client activate it from the
description.

```text
Use $design-workflow to polish the existing checkout without changing its layout.
```

```text
Add a billing-history screen that looks native to the current app.
```

```text
Replace the current visual direction, but keep the information architecture.
```

For ambiguous or high-impact work, the skill can create a route contract and
validate it without third-party dependencies:

```bash
python design-workflow/scripts/validate_route_contract.py contract.json
```

The contract's `meaningful_design_exists` field describes whether evidence
contains an established design system that must be preserved, not whether any
file exists. A wireframe can therefore use `create` with the field set to
`false`, while recording content order and information architecture in `fixed`.

## Development and verification

Use Python 3.11 or newer.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_project.py
agentskills validate design-workflow
python -m unittest discover -s tests -v
python scripts/package_skill.py
python scripts/package_project.py
```

`VERSION` is the release source of truth. Both package commands read it by
default; an optional `--version` must match it.

Deterministic unit and invariant checks cover structure, official Agent Skills
conformance, route contracts, fixture consistency, package allowlists, and
reproducible archives. They do not execute a model. Semantic behavior is tested
separately with `evals/semantic-smoke.json`; record a client run and grade it
with:

```bash
python scripts/grade_semantic_results.py path/to/client-result.json
```

Trigger/activation behavior is client- and model-dependent.
`evals/trigger-cases.json` contains balanced positive and near-miss prompts for
repeated client-specific activation tests; it is not a deterministic unit test.
Semantic forward tests likewise describe one recorded client, model, commit, and
suite revision. From v0.2.1 onward, raw results must follow
[`evals/semantic-result.schema.json`](evals/semantic-result.schema.json) and
record execution time, commit, skill version, runner, model, reasoning effort,
suite provenance, observed routes, and boundary rationales. See
[`evals/README.md`](evals/README.md) for the protocol.

The grader can verify field completeness, route equality, and a declared
boundary decision. It cannot independently infer that a response preserved the
boundary. A person or separate model must review each rationale (and any safely
recorded response excerpt) against the expected boundary.

### Current verification evidence

- project and link validator: passed
- official `agentskills` format validator: passed
- dependency-free unit tests: 22/22 passed for this revision
- historical v0.2.0 post-activation semantic forward test: 16/16 recorded across
  all eight routes; it was not rerun or relabeled for v0.2.1
- deterministic archive equality and root-directory checks: passed

The raw and graded forward-test records are stored in `evals/results/`. They
demonstrate route selection after the skill was loaded in the recorded run; they
do not claim universal activation accuracy or independently proven semantic
boundaries across every client or model.

Release skill ZIPs use an explicit file and directory allowlist. Generated
Python caches are excluded. Hidden files, temporary or backup files,
archives/checksums, symlinks, credential-like names, unexpected types, and
oversized files fail packaging instead of being silently shipped. Repository
docs, evals, and tests remain outside the runtime skill ZIP.

## Release

1. Update `CHANGELOG.md`.
2. Run all verification commands above.
3. Create and push the tag from `VERSION`, for example `git tag "v$(<VERSION)"`.
4. The release workflow requires `GITHUB_REF_NAME == "v" + VERSION`, validates
   the project, builds the deterministic archive, verifies the tag, and creates
   a GitHub Release with the archive and checksum. A mismatch stops the release.

## License and provenance

The project is Apache-2.0. Adapted material from Anthropic and Google is recorded
in `SOURCE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`. Required legal files are also
bundled inside the distributable skill.
