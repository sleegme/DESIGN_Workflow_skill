# Source and License Audit

Audit date: 2026-07-20
Release target: v0.2.1

## Repository license

The project and distributable `design-workflow/` package are Apache-2.0 licensed.
The release archive retains `LICENSE`, `NOTICE`, and
`THIRD_PARTY_NOTICES.md`.

## Incorporated sources

### Anthropic `frontend-design`

- Upstream: `anthropics/skills`, `skills/frontend-design/SKILL.md`
- License: Apache-2.0
- Adapted file: `design-workflow/references/frontend-design.md`
- Modifications: condensed, generalized beyond frontend work, restricted to new
  design and authorized redesign routes, and separated from preservation work
- Compliance: license and notices retained; the adapted file carries a prominent
  modification notice

### Google `stitch-skills`

- Upstream: `google-labs-code/stitch-skills`
- Relevant material: `design-md/SKILL.md` and `taste-design/SKILL.md`
- License: Apache-2.0
- Adapted file: `design-workflow/references/design-profile.md` and profile
  templates
- Modifications: removed Stitch-specific operations; added evidence confidence,
  conflicts, preservation boundaries, and unknowns
- Compliance: license and notices retained; the adapted file carries a prominent
  modification notice

## Original material

- eight-route intent model and preservation boundary
- mixed-route and partial-evidence rules
- evidence-security boundary
- route-contract format and validator
- evaluation fixtures, grading tool, project validator, tests, and packaging
  automation

## Excluded material

No traceable Canva text, template, code, or asset is included. Any future
third-party material must be audited against its exact source and license before
inclusion.
