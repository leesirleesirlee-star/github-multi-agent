## Summary

<!-- What changed and why, in 2-4 sentences. -->

## Issue / module

Closes #<!-- issue number -->

- Module label (exactly one): `module:<!-- id -->`
- Milestone/gate: `<!-- M0 | M1 | ... -->`

CI runs `scripts/check_modules.py`; a changed file outside the declared module
fails the `modules` job.

## Evidence

Commands run and observed output. For data, migrations or artifacts, include the
path and SHA-256.

```text
$ command
observed output
```

## Checks

- [ ] `ci / test`
- [ ] `ci / modules`
- [ ] `ci / codeowners`
- [ ] No file outside the declared module
- [ ] No secrets, credentials or private data
- [ ] Docs updated in the module's docs folder

## Impact

<!-- Which interface, contract, schema, data or user-visible behavior can change?
If none, say "none". -->

## Rollback

<!-- How to revert this change safely. -->
