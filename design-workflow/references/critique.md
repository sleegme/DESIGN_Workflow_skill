# Critique and Brand Check

Apply this reference to `critique` and `brand-check` routes.

## Preserve analysis-only scope

Do not edit, regenerate, or replace the artifact unless the user separately asks
for implementation. Recommendations do not authorize mutation.

## Evaluate against evidence

Use this order:

1. explicit user goal
2. project design contract or brand guide
3. current implementation and interaction behavior
4. approved references
5. medium-specific usability and accessibility requirements

Classify every finding:

- **Mismatch:** conflicts with a known rule or approved reference.
- **Defect:** clipping, unreadability, broken behavior, inaccessible state, or
  inconsistent implementation.
- **Weakness:** hierarchy, rhythm, specificity, or communication can improve.
- **Preference:** a subjective alternative with no governing requirement.

## Brand-check evidence

Check logo use, color roles and contrast, typography, shapes, icons, imagery,
motion, copy register, components, layout patterns, cross-medium consistency, and
unauthorized claims. If no brand or system evidence exists, report that the
result is a consistency critique rather than a compliance audit.

## Output

Lead with the highest-impact finding. Cite concrete visual, structural, or
behavioral evidence. For each recommendation, label the change as local,
system-level, redesign-only, or optional preference.
