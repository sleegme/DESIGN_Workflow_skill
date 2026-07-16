# Existing Design Preservation

This reference governs `preserve` and `expand`.

## Establish the preservation contract

Before changing anything, identify:

- authoritative artifact or implementation
- current hierarchy and layout relationships
- typography roles and scale
- palette, surface, border, depth, and shape language
- component patterns and interaction states
- content structure and terminology
- responsive behavior and accessibility behavior
- explicit user-approved differences

Treat these as fixed unless the task names them as changeable.

## Preserve by default

For a correction or implementation task:

- change the smallest coherent surface that solves the problem
- reuse existing tokens, components, spacing logic, and copy conventions
- keep unrelated layout, behavior, content, and decoration unchanged
- do not add visual furniture merely to make the work feel more designed
- do not replace a working pattern with a fashionable one without authorization
- do not convert every element into a card, chip, badge, panel, or glow
- preserve real content; do not fabricate metrics, testimonials, or product claims

## Expanding an existing system

When adding a new part:

1. Find at least two existing patterns that solve adjacent problems.
2. Derive the new element from those patterns.
3. Introduce a new token or component only when existing ones are insufficient.
4. Keep the new element's visual weight proportional to its importance.
5. Verify the addition in context, not as an isolated mockup.

## Correction hierarchy

Prefer corrections in this order:

1. incorrect implementation of an approved rule
2. token or component inconsistency
3. local layout or spacing issue
4. missing state or responsive behavior
5. structural change, only when explicitly authorized

## Validation checklist

- No unauthorized changes to information architecture.
- No new brand direction or aesthetic motif.
- No unrelated copy or feature additions.
- Existing interaction and responsive behavior still work.
- New elements match nearby patterns.
- Differences from the previous state can be explained by the task.
