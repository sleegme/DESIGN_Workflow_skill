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

## Development and verification

Use Python 3.11 or newer.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_project.py
agentskills validate design-workflow
python -m unittest discover -s tests -v
python scripts/package_skill.py --version 0.2.0
python scripts/package_project.py --version 0.2.0
```

The deterministic CI checks structure, official Agent Skills conformance, route
contract invariants, eval fixture quality, and reproducible packaging. Semantic
behavior is evaluated separately with `evals/semantic-smoke.json`; record a
client run and grade it with:

```bash
python scripts/grade_semantic_results.py path/to/client-result.json
```

Trigger behavior is client- and model-dependent. `evals/trigger-cases.json`
contains balanced positive and near-miss prompts for repeated client-specific
activation tests; it is not presented as a deterministic unit test.

### Current verification evidence

- project and link validator: passed
- official `agentskills` format validator: passed
- dependency-free unit tests: 13/13 passed
- independent post-activation semantic forward test: 16/16 passed across all
  eight routes
- deterministic archive equality and root-directory checks: passed

The raw and graded forward-test records are stored in `evals/results/`. These
results demonstrate route selection after the skill is loaded; they do not claim
universal activation accuracy across every client or model.

## Release

1. Update `CHANGELOG.md`.
2. Run all verification commands above.
3. Push a semantic-version tag such as `v0.2.0`.
4. The release workflow validates the project, builds the deterministic archive,
   verifies the tag, and creates a GitHub Release with the archive and checksum.

## License and provenance

The project is Apache-2.0. Adapted material from Anthropic and Google is recorded
in `SOURCE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`. Required legal files are also
bundled inside the distributable skill.
