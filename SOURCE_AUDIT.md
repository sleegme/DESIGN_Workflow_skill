# Source and License Audit

Audit date: 2026-07-16  
Release target: v0.1.0

## Repository license

The complete `design-workflow` package is distributed under Apache License 2.0.

## Incorporated sources

### Anthropic `frontend-design`

- Upstream: `anthropics/skills`, `skills/frontend-design/SKILL.md`
- License: Apache-2.0 (`skills/frontend-design/LICENSE.txt`)
- Use in this package: adapted and condensed into
  `references/frontend-design.md`
- Modifications:
  - generalized from frontend implementation to medium-neutral direction setting
  - loaded only for new design and explicit redesign routes
  - separated from preservation-only corrections
  - shortened to reduce context cost
- Compliance:
  - Apache-2.0 license included
  - attribution included in `THIRD_PARTY_NOTICES.md`
  - modified file carries a prominent modification notice

### Google `stitch-skills`

- Upstream: `google-labs-code/stitch-skills`
- Relevant upstream material:
  - `plugins/stitch-utilities/skills/design-md/SKILL.md`
  - `plugins/stitch-utilities/skills/taste-design/SKILL.md`
- License: Apache-2.0
- Use in this package: adapted concepts in
  `references/design-profile.md` and profile templates
- Modifications:
  - removed Stitch MCP, project IDs, upload, and tool-specific procedures
  - retained the tool-neutral pattern of descriptive language plus precise values
  - added evidence confidence, conflicts, preservation boundary, and unknowns
- Compliance:
  - Apache-2.0 license included
  - attribution included in `THIRD_PARTY_NOTICES.md`
  - modified file carries a prominent modification notice

## Excluded or unverified sources

### Canva

No traceable Canva text, template, code, or asset is incorporated in v0.1.0.
A Canva notice is therefore intentionally not included. False or speculative
attribution is worse than a precise source map.

Any future Canva-derived material must be audited against its exact source and
license before inclusion.

## Original material

The following are original to this package:

- intent routing and preservation boundary
- preservation and expansion procedure
- critique and brand-check procedure
- media translation procedure
- routing test cases and validation scripts
- README, CI, release, contribution, and security documentation

## Release conclusion

The v0.1.0 package is suitable for Apache-2.0 distribution provided that
`LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, and modification notices remain
with redistributed copies.
