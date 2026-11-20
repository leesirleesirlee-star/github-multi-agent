# AGENTS.md - rules for AI contributors

## Project

- **What this is:** <one sentence>.
- **Status:** <milestone>; <what is done and what is not>.
- **Team:** <N> contributors, one lead, one owner per module.
- **Source of truth:** `modules.json`.

## Read first

1. `START-HERE.md`
2. `AGENTS.md` (this file)
3. `modules.json`
4. `docs/plan/` and `docs/adr/`

## Write scope

1. Find your module in `modules.json`.
2. Only edit files under that module's `paths`.
3. If the change belongs to another module, open an issue; do not edit it.
4. Add exactly one `module:<id>` label to the issue and the PR.
5. Run `python scripts/check_modules.py --base origin/main` before pushing.

Do not edit `modules.json`, `.github/CODEOWNERS`, root configs or another
module's files unless you are the lead.

## Commands

```bash
<install command>
<lint command>
<test command>
python scripts/check_modules.py --base origin/main
python scripts/generate_codeowners.py --check
```

## Rules

1. One owner per module; no two agents write the same module.
2. One issue, one branch, one PR; keep the PR under 400 changed lines.
3. No direct push to `main`; no self-approval; no merge with a red check.
4. Do not weaken a test, contract, gate or check to get green.
5. No secrets, credentials, client data or private logs.
6. <domain-specific safety rule>
7. Missing is not passing: report `not_run` and the reason.
8. A claim needs a command, the observed output and a hash.

## Done means

- The requested behavior is complete and tested in the declared module.
- `ci / test`, `ci / modules` and `ci / codeowners` pass.
- The PR has one module label and an owner approval.
- Docs are updated in the module's docs folder.
- Evidence is in the PR.
