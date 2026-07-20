# Contributing

Keep the runtime skill focused on intent routing and change boundaries. Put human
documentation, release notes, tests, and evaluation results at the repository
root, not inside `design-workflow/`.

## Requirements

- Preserve the default rule: existing design is not redesign authorization.
- Keep `design-workflow/SKILL.md` concise and imperative.
- Link route-specific references directly from `SKILL.md`.
- Add realistic route and trigger cases for every behavior change.
- Treat recorded semantic results as evidence only when they come from a fresh
  client run.
- Keep runtime scripts dependency-free.
- Retain license, notice, and modification-attribution files.
- Do not add private project context, secrets, proprietary assets, or fabricated
  benchmark results.

## Verification

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_project.py
agentskills validate design-workflow
python -m unittest discover -s tests -v
python scripts/package_skill.py
python scripts/package_project.py
```

Open a pull request only after all commands pass and any changed semantic
behavior has a fresh forward-test result.
