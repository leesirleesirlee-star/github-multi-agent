# Contributing

Thanks for improving `github-multi-agent`.

## Before you start

1. Read [`SKILL.md`](SKILL.md) and the relevant file under `references/`.
2. Open an issue for a behavior change: module schema, matching rule, CLI
   contract, generated file format, or a new template.
3. Keep one logical change per PR.

## Checks

```bash
python -m pip install -r requirements-dev.txt
ruff check scripts
python scripts/validate_repo.py
python scripts/selftest.py
```

All four must pass. `validate_repo.py` also checks that the two generated
`CODEOWNERS` files are in sync with their registries.

## Rules

- Do not hand-edit `templates/CODEOWNERS` or
  `examples/example-project/.github/CODEOWNERS`; edit the registry and regenerate.
- The module registry schema is versioned. A breaking change bumps
  `schema_version` and is documented in `CHANGELOG.md`.
- Scripts use the Python standard library only, except `validate_repo.py` and the
  development tools (`pyyaml`, `ruff`).
- Keep the skill portable: no network, no service, no hardcoded absolute path.
- Do not add secrets, credentials or private data.
- Update `CHANGELOG.md` for a user-visible change.
- By contributing, you agree that your contribution is licensed under the MIT
  license in [`LICENSE`](LICENSE).

## Adding a reference or template

1. Add the file under `references/` or `templates/`.
2. Link it from `SKILL.md` and `README.md` if a user needs to find it.
3. If it is a template, make the placeholders obvious (`<project>`, `<module>`,
   `<owner>`).
4. Run the checks.

## Reporting a bug

Open an issue with the command you ran, the observed output, the expected output
and the Python version. Do not paste a key, token or private repository data.
