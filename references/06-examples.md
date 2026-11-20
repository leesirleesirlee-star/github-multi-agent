# 06 - Worked examples

## Example A: two people, three modules

```json
{
  "schema_version": 1,
  "default_reviewers": ["@alice", "@bob"],
  "modules": [
    {"id": "core", "title": "Domain", "owner": "@alice",
     "paths": ["src/core/", "tests/core/"], "may_depend_on": ["contract"]},
    {"id": "ui", "title": "Interface", "owner": "@bob",
     "paths": ["src/ui/", "tests/ui/"], "may_depend_on": ["contract"]},
    {"id": "contract", "title": "Schemas and docs", "owner": "@alice",
     "paths": ["schemas/", "docs/"], "may_depend_on": []}
  ]
}
```

- `default_reviewers` has both handles so either can approve the other.
- `contract` is small; the lead owns it and does not make it a second job.
- No `infra` module: root files are added to `contract` or a tiny `infra` later.

## Example B: five people, six modules

```json
{
  "schema_version": 1,
  "default_reviewers": ["@lead"],
  "modules": [
    {"id": "contract", "title": "Schemas and interfaces", "owner": "@lead",
     "paths": ["schemas/", "docs/interfaces/"]},
    {"id": "core", "title": "Domain", "owner": "@alice", "reviewers": ["@bob"],
     "paths": ["src/core/", "tests/core/"], "may_depend_on": ["contract"]},
    {"id": "api", "title": "Service API", "owner": "@bob", "reviewers": ["@alice"],
     "paths": ["src/api/", "tests/api/"], "may_depend_on": ["core"]},
    {"id": "ui", "title": "Web UI", "owner": "@carol",
     "paths": ["src/ui/", "tests/ui/"], "may_depend_on": ["contract"]},
    {"id": "data", "title": "Storage and migrations", "owner": "@dave",
     "paths": ["src/data/", "tests/data/", "migrations/"], "may_depend_on": ["contract"]},
    {"id": "infra", "title": "CI, scripts, docs", "owner": "@lead",
     "paths": [".github/", "scripts/", "docs/", "README.md", "modules.json"],
     "may_depend_on": []}
  ]
}
```

Why this shape:

- `contract` is separate from `core`; both `core` and `ui` may read it.
- `api` depends on `core`, not the reverse.
- `data` owns migrations, so schema changes and storage changes have one owner.
- `infra` is the catch-all for docs and root files; its paths are shorter than the
  specific modules, so the longest-prefix rule routes correctly.

## Example C: eight people, eight modules

```json
[
  {"id": "contract", "owner": "@lead", "paths": ["schemas/", "docs/interfaces/"]},
  {"id": "core-domain", "owner": "@alice", "paths": ["src/core/domain/"]},
  {"id": "core-runtime", "owner": "@bob", "paths": ["src/core/runtime/"]},
  {"id": "api-public", "owner": "@carol", "paths": ["src/api/public/"]},
  {"id": "api-internal", "owner": "@dave", "paths": ["src/api/internal/"]},
  {"id": "ui-web", "owner": "@erin", "paths": ["src/ui/web/"]},
  {"id": "ui-mobile", "owner": "@frank", "paths": ["src/ui/mobile/"]},
  {"id": "release", "owner": "@grace", "paths": ["tools/release/", "docs/release/"]}
]
```

Split `core` and `api` only because each half has a separate interface and a
separate writer. If the two halves change together every week, merge them.

## Good PR

```text
Title: feat(core): add retry policy for transient errors
Labels: module:core, type:feat
Closes: #42

## Summary
Adds a bounded retry policy; no public API change.

## Evidence
$ pytest tests/core -q
14 passed
$ python scripts/check_modules.py --base origin/main --labels "module:core,type:feat"
OK: every changed file matches the declared module

## Checks
- [x] test
- [x] modules
- [x] codeowners
- [x] no file outside core
- [x] docs updated in docs/core

## Impact
Retries are capped at 3; the contract is unchanged.

## Rollback
Revert this squash commit; no migration.
```

## Bad PRs

| Smell | Why it fails | Fix |
|---|---|---|
| `module:core` label, also edits `src/ui/` | scope check fails | split into two PRs |
| no module label | checker cannot route | add exactly one |
| 1,800 changed lines across five modules | unreviewable | split by module |
| edits `CODEOWNERS` by hand | generated file drifts | edit `modules.json`, regenerate |
| "tested manually" with no command | not evidence | paste the command and output |
| reviewer is the author | no independent check | another owner or lead reviews |

## Failure messages in context

```text
ERROR: outside module core: src/ui/app.ts -> ui
```

The PR is labelled `module:core` but changes a UI file. Either move the UI change
to a `module:ui` PR, or the change is genuinely cross-module and needs
`module:integration` and all owners' review.

```text
ERROR: unowned: docs/new-guide.md
```

`docs/new-guide.md` is not covered by a module path. Add `docs/` to `infra` (or
another owner) in `modules.json`, regenerate CODEOWNERS, and commit both.

```text
ERROR: stale: .github/CODEOWNERS
```

Someone edited CODEOWNERS by hand or changed `modules.json` without regenerating.
Run `python scripts/generate_codeowners.py` and commit the result.

```text
ERROR: exactly one module: label is required; found ['module:core', 'module:ui']
```

The PR has two labels. Keep the one that matches the majority of the diff, or
split the PR.
