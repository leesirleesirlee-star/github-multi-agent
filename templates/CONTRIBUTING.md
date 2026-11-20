# Contributing

## Before you start

1. Read `START-HERE.md` and `AGENTS.md`.
2. Find your module in `modules.json`.
3. Pick an issue with exactly one `module:<id>` label.

## Branch and PR

- Branch from the current `main`: `feat/<module>/<issue>-<slug>`.
- One issue, one module, one owner, one PR. Keep it under 400 changed lines.
- Add the same `module:<id>` label to the PR. CI checks that every changed file
  belongs to that module.
- Do not edit files outside your module. If the change needs another module,
  split the PR or ask the lead for `module:integration`.
- Fill in the PR template with commands run and observed output.

## Checks

```bash
<install command>
<lint command>
<test command>
python scripts/check_modules.py --base origin/main
python scripts/generate_codeowners.py --check
```

## Review

- The module owner reviews; the lead reviews gate and cross-module PRs.
- One approval plus green `ci / test`, `ci / modules` and `ci / codeowners` is
  required.
- Squash merge only. Delete the branch after merge.
- Never approve your own PR and never merge with a red required check.

## Evidence and safety

- A claim needs a command, an observed result and a hash.
- Do not weaken a test, contract, gate or check to get green.
- No secrets, credentials, client data or private logs.
- Report a missing check as missing; never as a pass.
