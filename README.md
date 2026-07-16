# design-workflow

**English** | [한국어](README.ko.md)

A medium-neutral Agent Skill for routing visual design work without accidentally
redesigning existing products.

The central guarantee is simple:

> When a meaningful design already exists, preserve it by default. Generate a new
> direction only for genuinely new work or an explicitly authorized redesign.

## Scope

The skill covers interfaces, websites, documents, slides, posters, brand assets,
images, data visualizations, video, and print.

It routes work into eight intents:

- preserve
- expand
- create
- redesign
- critique
- brand-check
- translate
- profile

## Installation

Place the complete `design-workflow/` directory in an Agent Skills-compatible
skill directory. The open standard uses a folder containing `SKILL.md`; many
clients support project-local `.agents/skills/design-workflow/`.

Keep the directory name exactly `design-workflow` because the Agent Skills
specification requires it to match the `name` field.

## Usage

Natural-language requests are enough:

```text
Polish the existing checkout flow without changing the layout.
```

```text
Add an account-security screen that matches the current app.
```

```text
We have no design yet. Create a visual direction for this scientific tool.
```

```text
Redesign the current landing page from scratch, but keep the content hierarchy.
```

```text
Extract a DESIGN.md from the current implementation and screenshots.
```

## Directory structure

```text
design-workflow/
├── SKILL.md
├── README.md
├── README.ko.md
├── LICENSE
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── SOURCE_AUDIT.md
├── CHANGELOG.md
├── RELEASE_CHECKLIST.md
├── CONTRIBUTING.md
├── SECURITY.md
├── references/
├── assets/
├── examples/
├── scripts/
├── tests/
└── .github/workflows/ci.yml
```

`SKILL.md` contains only the core route and boundary. Detailed instructions load
progressively from `references/`.

## Validation

Run the dependency-free checks:

```bash
python scripts/validate_skill.py .
python scripts/test_routing_cases.py

# Before packaging or installing the skill directory:
python scripts/validate_skill.py --strict-directory-name .
```

For an official format check, also run:

```bash
skills-ref validate .
```

The routing suite contains realistic positive, negative, ambiguous, and
cross-medium prompts. The included v0.1.0 report is an authoring-session dry run,
not a claim of identical behavior across every model or client.

## Design boundary

The following do not authorize redesign by themselves:

- improve
- polish
- modernize
- clean up
- make it better
- add a feature
- fix responsiveness
- align with the brand

A redesign requires explicit replacement language or a clearly authorized
structural/visual change.

## Project-specific rules

This repository intentionally contains no project, company, palette, or product
context. Put project-specific rules in the target repository's `DESIGN.md`,
`.design/PROFILE.md`, brand guide, component library, or equivalent source of
truth.

## License and sources

The package is Apache-2.0. Adapted portions from Anthropic and Google sources are
identified in `SOURCE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`. No unverified Canva
material is included.
