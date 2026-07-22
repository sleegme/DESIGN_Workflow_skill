# design-workflow

**English** | [한국어](README.ko.md)

`design-workflow` helps ChatGPT decide what should stay, what may change, and
whether a design should be improved or created from scratch before the actual
work begins.

## What changes after installation

The skill guides decisions about visual work. It does not draw, render, or edit
an artifact by itself, and installing it does not automatically restyle every
output or change the ChatGPT interface. ChatGPT or another connected image,
web, document, slide, design, browser, or code workflow performs the actual
work.

In technical terms, `design-workflow` is an Agent Skill that provides routing,
change-boundary guardrails, and compact positive design judgment. It classifies
a request as preserving, improving, extending, creating, or explicitly
redesigning an artifact before an execution tool takes over. Its central rule is
simple: preserve a meaningful existing design unless the user clearly
authorizes replacement. For new design, authorized redesign, and design-bearing
translation, v0.3.0 also establishes a coherent direction, interprets references
as systems, checks generic AI-design defaults, and applies one bounded critique
and repair pass.

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
├── evals/                       # route/boundary and separate design-quality cases
├── VERSION                      # single release-version source of truth
├── scripts/                     # project validation, grading, and packaging
├── tests/                       # dependency-free unit tests
└── .github/workflows/           # CI and tagged release automation
```

Keeping the skill in a literal `design-workflow/` directory makes the package
conform to the Agent Skills requirement that the parent directory match the
frontmatter `name`.

## Installation in ChatGPT

Where skill creation or upload is available in your ChatGPT environment:

1. Open **Plugins / Skills**.
2. Choose the option to create a skill or upload one.
3. Download and select `design-workflow-<version>.zip` from the corresponding
   GitHub Release.
4. Review the skill and complete the installation.

Skill availability and exact labels can vary by client, account, and workspace
configuration. These steps do not imply that every ChatGPT environment supports
skill upload.

On macOS and Windows, there is no separate native `design-workflow` application
to install for ChatGPT use. Add the skill through a compatible ChatGPT Skills
interface.

## Installation in Codex

Install only the nested `design-workflow/` directory into the skills directory
used by Codex. Do not install the repository root.

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

## Verify the installation

Try this copyable prompt without asking the client to edit anything:

```text
Use $design-workflow to classify this request without editing:
“Polish the existing dashboard while preserving its layout and brand identity.”
```

Wording varies by client and model, but an illustrative result is:

```text
Selected route: preserve
Fixed constraints: existing layout and brand identity
Changeable areas: local visual polish that does not alter those constraints
Redesign authorized: no
```

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

```text
Create a realistic repair-workshop photograph. Set a compact visual direction,
use only the generated-image guidance, and report the single critique repair.
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

Positive visual-generation behavior uses the separate
`evals/design-quality-cases.json` suite. Run matching no-skill and skill-enabled
tasks in the same real client, retain both artifacts, have an independent
reviewer record concrete evidence, and validate the record with:

```bash
python scripts/grade_design_quality_results.py \
  path/to/client-design-quality.raw.json
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

The design-quality grader is likewise a structural record check. It does not
inspect pixels or establish universal aesthetic improvement. Its protocol and
schema explicitly require independent visual review and preserve real
ChatGPT-/Gemini-class comparisons as external client evidence.

### Current verification evidence

- project and link validator: passed
- official `agentskills` format validator: passed
- dependency-free unit tests: 26/26 passed for this revision
- historical v0.2.0 post-activation semantic forward test: 16/16 recorded across
  all eight routes; it was not rerun or relabeled for v0.2.1, v0.2.2, or v0.3.0
- deterministic archive equality and root-directory checks: passed
- ChatGPT-class and Gemini-class v0.3.0 before/after visual runs: pending external
  client execution; no result is fabricated from structural checks

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

1. Update `VERSION` and `CHANGELOG.md`.
2. Run all verification commands above.
3. Create and push the tag from `VERSION`, for example `git tag "v$(<VERSION)"`.
4. The release workflow requires `GITHUB_REF_NAME == "v" + VERSION`, validates
   the project, builds the deterministic archive, and verifies the tag. It
   creates a GitHub Release when none exists or replaces the ZIP and checksum
   assets on a rerun. A mismatch stops the release.

## FAQ

### I installed it, but nothing changed

That can be expected. The skill does not change the ChatGPT interface or apply
a default visual style. It guides a compatible workflow when a request needs a
visual-design decision. Use the verification prompt above to test it explicitly.

### Does it create designs by itself?

No. It selects a route and defines what must stay fixed or may change. ChatGPT
or a connected execution workflow creates or edits the artifact.

### Can it make a new design when no draft exists?

It can select the `create` route and establish a direction when no meaningful
design exists. The connected execution workflow then makes the design.

### Is it more useful for existing designs?

It is especially useful when an existing design must be protected from
accidental redesign, but it also guides new work, extensions, critiques, brand
checks, translations, and design-profile extraction.

### How do I install it in ChatGPT or on a Mac?

Use the compatible ChatGPT Skills interface and upload the release ZIP as
described above. A Mac does not require a separate native installation for this
skill. For Codex, use the separate filesystem instructions.

## License and provenance

The project is Apache-2.0. Adapted material from Anthropic and Google is recorded
in `SOURCE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`. Required legal files are also
bundled inside the distributable skill.
