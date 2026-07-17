# Routing Reference

Read this file when the route is ambiguous, mixed, or dependent on incomplete
evidence.

## Decision order

1. If the user asks only for analysis, choose `critique` or `brand-check`.
2. If the deliverable is a derived design contract, choose `profile`.
3. If a specific source artifact must be recomposed for a new delivery
   constraint, choose `translate`.
4. Determine whether a meaningful existing design exists.
5. If no meaningful design exists, choose `create`.
6. If the user explicitly authorizes replacement, choose `redesign`.
7. If the task adds a sibling part that must join the current system, choose
   `expand`.
8. Otherwise, choose `preserve`.

## Meaningful existing design

Treat a design as meaningful when available evidence establishes at least two of
the following and the user has not asked to discard them:

- content hierarchy or information architecture
- recurring layout or spacing logic
- typography, color, shape, imagery, or motion language
- component and interaction patterns
- brand identity or campaign identity
- an approved editable artifact, implementation, template, or design contract

Treat partial evidence dimension by dimension. A wireframe can fix hierarchy
while leaving visual language open. A brand guide can fix identity while leaving
page composition open. Record these as separate fixed and changeable fields.

## Explicit redesign authorization

Accept authorization when the request clearly permits replacement, for example:

- redesign from scratch
- replace the current visual direction
- rebrand the product
- completely rethink the layout
- discard the existing structure
- make it feel entirely new even if that means replacing the current system

Do not require a magic word. Require clear permission to replace a named or
reasonably implied design dimension.

## Route boundaries

### Preserve versus redesign

Choose `preserve` for polish, modernization, corrections, implementation, and
accessibility fixes when the request does not authorize system replacement.
Under `preserve`, modernization may refine density, consistency, type usage,
spacing, contrast, and responsive behavior using the established system.

### Expand versus translate

- Choose `expand` when creating a new sibling artifact or state that joins an
  existing product, deck, campaign, or component family.
- Choose `translate` when adapting a particular source artifact or content set to
  a new medium, aspect ratio, platform, interaction mode, or reading distance.
- For a campaign extension that also adapts a particular source, use `expand` as
  primary and `translate` as secondary.

### Critique versus brand-check

- Choose `critique` for usability, hierarchy, communication, accessibility, or
  comparative design analysis.
- Choose `brand-check` when a brand guide, design system, approved reference, or
  cross-artifact consistency rule is the governing evidence.

## Mixed requests

Select one primary route and list secondary routes in execution order. Apply the
strictest mutation boundary until the user authorizes more.

Examples:

- Audit a dashboard, then fix spacing only: `preserve` primary, `critique`
  secondary first.
- Extract the current system, then add a settings screen: `expand` primary,
  `profile` secondary first.
- Keep information architecture but replace visual language: `redesign` with
  information architecture fixed.
- Turn a desktop dashboard into a printable report: `translate` with identity
  and content priority fixed.

## Ambiguity protocol

Ask a question only when the missing answer would materially change the artifact
or authorize irreversible structural drift. Otherwise choose the safer route,
record the assumption, and continue with the reversible portion.

When escalation is required:

1. Name the concrete conflict.
2. State the smallest additional authorization needed.
3. Offer the safe result that remains within scope.
