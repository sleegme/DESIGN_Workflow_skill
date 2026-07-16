---
name: design-workflow
description: Use this skill for visual design work across interfaces, websites, documents, slides, posters, brand assets, images, data visualizations, video, and print. Use it when creating a design, extending or revising an existing design, explicitly redesigning, critiquing, checking brand consistency, translating between media, or extracting a reusable DESIGN.md/profile. When an artifact already exists, default to preserving its established design unless the user explicitly authorizes a redesign.
license: Apache-2.0
compatibility: Agent Skills-compatible clients. Image, browser, design, document, slide, or code tools are optional and depend on the task.
metadata:
  author: sleegme
  version: "0.1.0"
  source-audit: SOURCE_AUDIT.md
---

# Design Workflow

Route design work by **user intent and existing evidence**, not by medium or tool.

## Non-negotiable boundary

When a design already exists, preserve its established visual language, hierarchy,
layout logic, interaction model, content structure, and brand cues unless the
user explicitly authorizes replacing them.

Words such as *improve*, *polish*, *clean up*, *modernize*, *make it better*,
*fix*, *align*, or *add a feature* do **not** authorize a redesign.

## Route first

Classify the task before editing or generating anything.

| Route | Use when | Default mutation |
|---|---|---|
| `preserve` | Correct, polish, implement, or revise an existing artifact without replacing its design | Local changes only |
| `expand` | Add a screen, section, component, slide, page, or state that must match an existing system | New parts inherit the existing system |
| `create` | No meaningful design exists and the user asks for a new one | Establish a new direction |
| `redesign` | The user explicitly asks to replace, rethink, rebrand, or substantially restructure an existing design | Authorized structural and visual change |
| `critique` | Analyze, compare, diagnose, or recommend without editing | No mutation |
| `brand-check` | Audit consistency against brand or design-system evidence | No mutation unless separately requested |
| `translate` | Adapt an existing design to another medium, aspect ratio, platform, or format | Preserve identity; adapt constraints |
| `profile` | Extract or generate `DESIGN.md` or `.design/PROFILE.md` from evidence | Create documentation, not a redesign |

Read [references/routing.md](references/routing.md) when the route is ambiguous.

## Evidence order

Use the strongest available source of truth in this order:

1. The user's explicit request and authorized scope.
2. Existing artifact, implementation, or editable source.
3. Project design contract such as `DESIGN.md`, `.design/PROFILE.md`, brand guide,
   component library, tokens, or templates.
4. Approved references and screenshots.
5. General design judgment.

Do not let a generic design reference override an established project design.

## Conditional references

Load only the reference needed for the selected route.

- `preserve` or `expand`: read
  [references/preservation.md](references/preservation.md).
- `create`: read [references/frontend-design.md](references/frontend-design.md).
- `redesign`: read both preservation and frontend-design references. First record
  what is being intentionally replaced and what still must remain.
- `critique` or `brand-check`: read
  [references/critique.md](references/critique.md).
- `translate`: read
  [references/media-translation.md](references/media-translation.md).
- `profile`: read
  [references/design-profile.md](references/design-profile.md) and use the
  appropriate template in [assets/](assets/).

## Working procedure

1. **Inspect** the current artifact and governing project rules before proposing
   changes.
2. **Route** the task using the table above.
3. **Declare the boundary** internally: what is fixed, what may change, and what
   evidence governs.
4. **Plan at the right scale**:
   - local correction for `preserve`
   - pattern extension for `expand`
   - deliberate direction setting for `create`
   - explicit replacement map for `redesign`
5. **Execute** without adding unrelated decoration, features, copy, or structure.
6. **Validate** against the route:
   - preservation: no unauthorized structural or identity drift
   - expansion: new work reads as part of the same system
   - creation/redesign: direction is specific to the subject, not a generic template
   - critique/brand-check: findings are evidence-based and do not silently mutate
   - translation: identity survives the medium change
   - profile: rules are derived, precise, and uncertainty is marked
7. **Report** what changed, what was preserved, and any unverified assumptions.

## Gotchas

- An implementation request is not permission to invent a new design.
- A new page inside an existing product is usually `expand`, not `create`.
- A reference image is evidence, not automatic permission to copy unrelated
  structure or branding.
- If project documentation and the implementation disagree, report the conflict;
  do not silently choose the more aesthetically appealing source.
- Do not load the new-design reference for a narrow preservation-only task.
- Never introduce project-specific names, palettes, products, or organizational
  context into this reusable skill.
