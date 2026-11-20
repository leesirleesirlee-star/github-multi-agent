# 02 - Module registry, CODEOWNERS and the CI scope check

## Files

| File | Role |
|---|---|
| `modules.json` | the single source of truth |
| `scripts/module_registry.py` | load, validate, match, render CODEOWNERS |
| `scripts/generate_codeowners.py` | write or check `.github/CODEOWNERS` |
| `scripts/check_modules.py` | fail a PR whose files fall outside its module |
| `.github/CODEOWNERS` | generated review routing; do not edit by hand |

## Registry schema

```json
{
  "schema_version": 1,
  "module_label_prefix": "module:",
  "integration_label": "module:integration",
  "default_reviewers": ["@lead"],
  "ignored_prefixes": ["var/", ".venv/", "__pycache__/"],
  "modules": [
    {
      "id": "core",
      "title": "Core domain",
      "owner": "@alice",
      "reviewers": ["@bob"],
      "paths": ["src/core/", "tests/core/"],
      "may_depend_on": ["contract"],
      "forbidden_paths": ["src/ui/"],
      "interfaces": ["CoreService"],
      "gate": "M1",
      "notes": "No UI imports."
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `schema_version` | yes | bump on a breaking schema change |
| `module_label_prefix` | no | default `module:` |
| `integration_label` | no | default `module:integration` |
| `default_reviewers` | no | CODEOWNERS `*` rule; usually the lead |
| `ignored_prefixes` | no | runtime/tooling paths excluded from the check |
| `modules` | yes | 1-12 modules is a healthy range for a small team |
| `id` | yes | kebab-case, unique, matches `module:<id>` |
| `title` | yes | human label |
| `owner` | yes | one GitHub handle, `@name` or `@org/team` |
| `reviewers` | no | backup reviewers, not co-writers |
| `paths` | yes | directory prefixes ending `/`, or exact file paths |
| `may_depend_on` | no | allowed module ids; documentation and review input |
| `forbidden_paths` | no | paths this module must never read/import |
| `interfaces` | no | names of the artifacts this module owns |
| `gate` | no | free-form milestone, for example `M0` or `G2` |
| `notes` | no | one-line constraint |

## Path rules

- Directory: `src/core/` (trailing slash).
- Exact file: `README.md` (no trailing slash).
- Repository-relative only; no `C:\`, no `..`, no leading `./` after load.
- Use `/`, not `\`, so the same registry works on Linux CI and Windows.
- Every tracked path should match exactly one module. Add a catch-all `infra`
  module for root files and docs, then override it with longer prefixes.

## Matching algorithm

1. Normalize: `\` to `/`, strip `./`, strip a leading `/`.
2. Exact file rules win.
3. Otherwise, among directory prefixes, the **longest** prefix wins.
4. A tie between two modules is a registry bug; `validate_registry` fails.
5. No match = `unowned`; the check fails.

Example:

```text
docs/                      infra
docs/interfaces/           contract   (longer prefix wins)
src/core/app.py            core
src/core/app.py            core       (exact file if listed)
src/corex/app.py           unowned    (no prefix match)
```

## Dependency direction

`may_depend_on` is a review rule, not an import firewall in v1. State it anyway,
because it tells reviewers what a module is allowed to know.

Typical shape:

```text
contract  <-  core  <-  api  <-  ui
     ^          ^
     |          |
   infra      docs
```

- `contract` has no dependencies; everyone may read it.
- `core` reads `contract`, never `ui`.
- `ui` reads `contract`, never `core` internals.
- `infra` reads nothing; it owns CI, scripts and docs.

Put the forbidden direction in `forbidden_paths` too, so a reviewer can see it
without opening a design doc.

## Generate CODEOWNERS

```bash
python scripts/generate_codeowners.py            # write .github/CODEOWNERS
python scripts/generate_codeowners.py --check    # CI: fail if stale
python scripts/generate_codeowners.py --stdout   # inspect
```

The output is deterministic:

1. default reviewers on `*`;
2. path rules sorted shortest-first so the last match is the most specific;
3. exact file rules after a directory rule of the same length.

Never edit `.github/CODEOWNERS` by hand. `ci / codeowners` fails when it differs
from the registry.

## Check a PR

```bash
# ownership only
python scripts/check_modules.py --base origin/main

# ownership + declared module label
python scripts/check_modules.py \
  --base origin/main \
  --labels "module:core,type:feat"
```

Exit codes: `0` pass, `1` ownership/scope/label error, `2` invalid registry.

The checker requires **exactly one** `module:<id>` label when `--labels` is
provided. `module:integration` is the only wildcard; reserve it for the lead's
gate PRs and still require review.

## CI jobs

```yaml
modules:
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }
    - run: git fetch --no-tags origin ${{ github.base_ref }}
    - run: python scripts/check_modules.py --base FETCH_HEAD --labels "${{ join(github.event.pull_request.labels.*.name, ',') }}"

codeowners:
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - run: python scripts/generate_codeowners.py --check
```

Make `ci / test`, `ci / modules` and `ci / codeowners` required checks in the
`main` ruleset.

## Add, rename or remove a module

1. Write an ADR: why the boundary changes, who owns it, which paths move.
2. Edit `modules.json`; keep the id stable unless the change is intentional.
3. Regenerate CODEOWNERS: `python scripts/generate_codeowners.py`.
4. Move files in a dedicated PR; do not mix a move with behavior changes.
5. Update the project board's `Module` field and the labels.
6. Run the negative test once for the new module.

Renaming a module changes the label, the path rules and CODEOWNERS. Do it in one
PR, or the CI check fails for the transition period.

## Failure messages

| Message | Meaning | Fix |
|---|---|---|
| `unowned: path` | no module claims the path | add it to a module or delete it |
| `outside module X: path -> Y` | PR label and file disagree | move the file, split the PR, or ask for integration |
| `missing module label` | zero `module:*` labels | add exactly one |
| `multiple module labels` | two or more | keep the one matching the files |
| `unknown module label` | label has no module in the registry | add the module or fix the label |
| `declared module X but no changed file belongs to it` | label is unrelated to the diff | fix the label or the branch |
| `ambiguous path` | two modules claim the same prefix | fix the registry |
| `stale: .github/CODEOWNERS` | generated file drifted | run the generator and commit |

## Generated and ignored files

- `var/`, `.venv/`, `__pycache__/`, `.pytest_cache/` are ignored by default; do
  not add them to modules.
- A generated file that is committed needs an owner. Usually the module that
  generates it owns it.
- Do not hand-edit generated files; regenerate and commit the diff.

## Monorepos

If the repository contains several applications, make each application a module
or a small group of modules, and add one `platform`/`infra` module for shared
CI, scripts and docs. Do not create a module per package unless the packages have
different owners and interfaces.

## Security

- `modules.json` and `CODEOWNERS` are public review metadata; never put secrets
  in them.
- A module owner is a review role, not a permission grant. GitHub write access is
  separate.
- The CI module job only reads the registry and the diff; it does not need a
  token beyond `contents: read`.
