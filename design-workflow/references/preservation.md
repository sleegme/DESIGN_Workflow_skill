# Existing Design Preservation

Apply this reference to `preserve` and `expand` routes.

## Establish the preservation contract

Identify the evidence and classify each dimension as fixed, locally adjustable,
or unknown:

- content hierarchy and terminology
- layout relationships and responsive behavior
- typography roles and scale
- palette, surface, border, depth, and shape language
- components, interaction patterns, and states
- imagery, iconography, data visualization, and motion
- accessibility behavior
- explicit user-approved differences

Do not promote an isolated accident into a system rule. Use at least two
representative examples before inferring a recurring pattern when possible.

## Preserve route

1. Locate the smallest coherent source of the problem.
2. Reuse existing tokens, components, templates, spacing logic, and copy
   conventions.
3. Correct implementation defects before proposing new patterns.
4. Keep unrelated layout, content, behavior, and decoration unchanged.
5. Verify the result beside the previous state and its neighboring context.

Avoid decorative additions that do not solve the request. Do not convert every
element into a card, chip, badge, panel, gradient, or glow. Do not replace a
working pattern merely because another pattern is fashionable.

## Expand route

1. Find at least two adjacent patterns that solve similar problems.
2. Derive the new part from those patterns.
3. Introduce a token or component only when existing options are insufficient.
4. Keep visual weight proportional to content importance.
5. Test the addition inside the existing artifact, including empty, loading,
   error, focus, and responsive states where applicable.

## Correction order

Prefer changes in this order:

1. incorrect implementation of an approved rule
2. token or component inconsistency
3. local layout, type, or spacing defect
4. missing interaction, accessibility, or responsive state
5. structural change explicitly authorized by the user

## Validation

- Preserve information architecture unless authorized otherwise.
- Introduce no new brand direction or unrelated motif.
- Add no fabricated content, features, claims, or data.
- Keep existing interaction and accessibility behavior working.
- Make new elements read as part of the same system.
- Explain every intentional difference through the user request or governing
  evidence.
