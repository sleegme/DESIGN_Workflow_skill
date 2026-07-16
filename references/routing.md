# Routing Reference

Use this file only when the main route is ambiguous.

## Decision order

1. Is the user asking only for analysis?
   - Yes: `critique` or `brand-check`.
2. Is the output a design profile or design-system document?
   - Yes: `profile`.
3. Is an existing artifact being adapted to another medium or format?
   - Yes: `translate`.
4. Does a meaningful existing design exist?
   - No: `create`.
5. Did the user explicitly authorize replacement of the existing direction,
   structure, brand, or visual language?
   - Yes: `redesign`.
6. Is the user adding a new part that must belong to the current system?
   - Yes: `expand`.
7. Otherwise: `preserve`.

## Boundary phrases

These phrases normally mean `preserve`:

- improve, polish, refine, clean up, modernize
- fix spacing, typography, responsiveness, hierarchy, contrast
- implement the approved design
- align with the reference or brand guide
- make this less AI-generated
- add a field, state, screen, section, chart, or slide while keeping the style

These phrases normally mean `redesign`:

- redesign from scratch
- replace the current visual direction
- rebrand the product
- completely rethink the layout
- discard the existing structure
- explore a fundamentally different concept

`Modernize` alone is not enough to authorize redesign.

## Mixed requests

When a request combines routes, choose one primary route and preserve the stricter
boundary.

Examples:

- "Audit this dashboard and then fix only the spacing issues"
  → primary `preserve`; critique is the first step.
- "Extract the current design system, then add a matching settings screen"
  → `profile`, then `expand`.
- "Keep the information architecture but redesign the visual language"
  → `redesign`; information architecture remains fixed.
- "Turn this desktop dashboard into a printable report"
  → `translate`; do not apply a new brand direction.

## Escalation

If the requested result cannot be achieved without crossing the current boundary:

1. Explain the concrete conflict.
2. State the smallest additional authorization needed.
3. Continue with the safe portion instead of silently redesigning.
