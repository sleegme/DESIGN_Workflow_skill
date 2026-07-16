# Design Profile Extraction and Generation

> Source and modification notice: This file adapts concepts from Google
> `stitch-skills` design-system skills, licensed under Apache-2.0. It removes
> Stitch-specific MCP operations and makes the workflow tool-neutral. See
> `SOURCE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`.

This reference governs `profile`.

## Choose the output

- Use root `DESIGN.md` when the project treats the design contract as a primary
  repository document.
- Use `.design/PROFILE.md` when the profile should remain tool-agnostic,
  optional, or nested.
- Do not create both unless the project already uses both for distinct purposes.

## Evidence collection

Inspect representative artifacts, implementation, tokens, styles, components,
templates, brand guides, and interaction states.

Record exact evidence where possible:

- color values and functional roles
- type families, sizes, weights, line heights, and roles
- spacing and layout patterns
- shape, border, depth, and material behavior
- component variants and interaction states
- imagery, iconography, data visualization, and motion
- responsive and accessibility behavior
- prohibited patterns and known exceptions

## Synthesis rules

- Describe visual rules in natural language and include precise values.
- Explain function, not just appearance.
- Distinguish observed facts from inferred patterns.
- Mark unknown or conflicting evidence instead of inventing a rule.
- Do not turn a one-off accident into a system rule.
- Do not use profile generation as an excuse to redesign the project.

## Required sections

Use the template in `assets/DESIGN.template.md` or
`assets/PROFILE.template.md`.

At minimum include:

1. scope and source evidence
2. visual atmosphere and principles
3. color roles
4. typography roles
5. layout and spacing
6. shapes, depth, and materials
7. components and states
8. imagery, iconography, data, and motion
9. responsive and accessibility behavior
10. preservation rules and anti-patterns
11. unknowns and conflicts
