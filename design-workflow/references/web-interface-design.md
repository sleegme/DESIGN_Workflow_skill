# Web and Interface Composition Guidance

Load this file only for web or interface composition after loading
`visual-direction.md`.

## Organize behavior and content

- Preserve or deliberately establish information architecture before styling.
  Make primary and secondary actions reflect task priority.
- Define container widths, grid relationships, alignment anchors, and spacing
  intervals; use whitespace to group and separate content.
- Keep display, heading, body, label, control, and data typography roles
  consistent across states.
- Repeat components when semantics repeat and introduce an exception only when
  content, state, or task priority justifies it.
- Treat responsive behavior as recomposition: reprioritize, reflow, crop,
  disclose, or change controls intentionally instead of merely stacking boxes.
- Include relevant loading, empty, error, focus, hover, active, disabled, and
  long-content states.
- Avoid a generic SaaS dashboard of equal rounded cards when the content calls
  for a table, timeline, canvas, document, feed, map, or other native structure.

During the one critique pass, inspect hierarchy and CTA priority at representative
wide and narrow widths. Repair the highest-impact composition or state failure
once without drifting beyond the route contract.
