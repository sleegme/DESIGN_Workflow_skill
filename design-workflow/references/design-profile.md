# Design Profile Extraction

> Source and modification notice: This file adapts concepts from Google
> `stitch-skills` design-system skills, licensed under Apache-2.0. It removes
> Stitch-specific operations and makes the workflow tool-neutral. See
> `THIRD_PARTY_NOTICES.md` in the skill directory.

Apply this reference to the `profile` route.

## Select one output

- Use root `DESIGN.md` when the design contract is a primary repository rule.
- Use `.design/PROFILE.md` when the profile is optional, tool-neutral, or nested.
- Do not create both unless the project already gives them distinct purposes.

## Collect evidence

Inspect representative artifacts, implementation, tokens, styles, components,
templates, brand guides, and interaction states. Record exact evidence for:

- color values and functional roles
- type families, sizes, weights, line heights, and roles
- spacing, grid, containment, and responsive patterns
- shapes, borders, depth, materials, and motion
- component variants and interaction states
- imagery, iconography, and data visualization
- accessibility behavior, exceptions, and prohibited patterns

## Synthesize conservatively

- Describe function as well as appearance.
- Separate observed facts from inferred patterns.
- Assign confidence and cite the source artifact or code location.
- Mark unknown or conflicting evidence instead of inventing rules.
- Do not treat a one-off accident as a system rule.
- Do not use profile generation as redesign permission.

Use [../assets/DESIGN.template.md](../assets/DESIGN.template.md) or
[../assets/PROFILE.template.md](../assets/PROFILE.template.md). Remove sections
that do not apply, but retain evidence, preservation, accessibility, and unknowns.
