# Contributing

Contributions should improve reusable design-routing behavior rather than add a
specific project's visual rules.

## Requirements

- Keep `SKILL.md` concise and route-focused.
- Put conditional detail in one-level `references/` files.
- Add or update realistic cases for every routing change.
- Preserve the default rule: existing design is not redesign authorization.
- Do not add company, product, campaign, palette, or private workflow context.
- Audit every copied or adapted source before inclusion.
- Keep scripts dependency-free unless a dependency is clearly justified.

## Validation

```bash
python scripts/validate_skill.py .
python scripts/test_routing_cases.py
```

Run the checks before opening a pull request.
