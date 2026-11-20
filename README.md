# github-multi-agent

![ci](https://github.com/leesirleesirlee-star/github-multi-agent/actions/workflows/ci.yml/badge.svg)

A portable **DeepSeek Harness skill** for running a shared GitHub repository with
**precise module ownership** instead of informal "who usually edits this" rules.

It gives a team of 2-10 people - or 2-10 agents - four checkable controls:

1. a `modules.json` registry - one owner, path scope, interface and gate per module;
2. generated `CODEOWNERS` - review routing that cannot drift;
3. a CI scope check - a PR that changes files outside its declared module fails;
4. branch, project and handoff templates - the process around the checks.

The same rules work for human and agent teams: an agent is a contributor with a
recorded write scope, not a free-form editor.

**Version:** 0.1.0 (2026-11-20).

## Install

DSH discovers skills from these roots:

| Scope | Path |
|---|---|
| Project | `<project>/.dsh/skills/github-multi-agent/` |
| Project (shared) | `<project>/.agents/skills/github-multi-agent/` |
| User | `~/.dsh/skills/github-multi-agent/` |

From this repository:

```bash
git clone https://github.com/leesirleesirlee-star/github-multi-agent.git
cp -r github-multi-agent <project>/.dsh/skills/
```

Windows:

```powershell
Copy-Item -Recurse .\github-multi-agent <project>\.dsh\skills\
```

No restart is needed; the filesystem provider watches the root. Verify with a new
session, or load it by name:

```text
skill github-multi-agent
```

To make it available in every project, copy it to `~/.dsh/skills/` (Windows:
`C:\Users\<you>\.dsh\skills\`).

## Quick start

In the target project:

```bash
# 1. copy scripts/ and templates/modules.json into the project
# 2. edit modules.json: ids, owners, paths
# 3. generate and check review routing
python scripts/generate_codeowners.py
python scripts/generate_codeowners.py --check

# 4. create module labels (requires gh; dry run by default)
python scripts/sync_labels.py
python scripts/sync_labels.py --apply

# 5. add templates/ci.yml as .github/workflows/ci.yml
# 6. protect main; see references/03-github-setup.md
```

Then run the negative test: change a file in module A, label the PR `module:B`,
and confirm `ci / modules` fails. A workflow you have not tested negatively is a
workflow you do not know.

## What is inside

| Path | Contents |
|---|---|
| `SKILL.md` | the model-facing playbook and the rules |
| `references/01-principles.md` | why module ownership works; anti-patterns |
| `references/02-module-registry.md` | schema, matching, dependency rules, CI |
| `references/03-github-setup.md` | labels, ruleset, project, first issues, negative test |
| `references/04-scaling-roles.md` | 2, 3, 5, 8, 10 contributors and agent teams |
| `references/05-handoff-and-conflicts.md` | onboarding, migration, freeze, rework |
| `references/06-examples.md` | worked module maps and PR examples |
| `scripts/module_registry.py` | load, validate, match, render CODEOWNERS |
| `scripts/generate_codeowners.py` | write/check `.github/CODEOWNERS` |
| `scripts/check_modules.py` | CI scope and label check |
| `scripts/sync_labels.py` | create `module:<id>` labels from the registry |
| `scripts/validate_repo.py` | validate this package: frontmatter, syntax, links, generated files |
| `scripts/selftest.py` | no-dependency self-test for the registry and checkers |
| `templates/` | modules, CI, PR/issue forms, START-HERE, AGENTS, MIGRATION |
| `examples/example-project/` | a four-module project used by the self-test |

Generated files:

- `templates/CODEOWNERS` is generated from `templates/modules.json`.
- `examples/example-project/.github/CODEOWNERS` is generated from the example
  registry.

Edit the registry, not the generated file.

## Verify

```bash
python -m pip install -r requirements-dev.txt
ruff check scripts
python scripts/validate_repo.py
python scripts/selftest.py
```

Expected:

```text
repo validation OK
selftest OK
```

The self-test covers longest-prefix matching, unowned files, a file outside the
declared module, missing/duplicate labels, integration mode, ignored paths, and
CODEOWNERS generation order. `validate_repo.py` checks the skill frontmatter,
JSON/YAML syntax, Markdown links and generated CODEOWNERS in sync.

## How it works

A **module** is one owner + one path scope + one public interface + one gate.

- Every tracked path belongs to exactly one module.
- A PR carries exactly one `module:<id>` label; every changed file must belong to
  that module.
- `module:integration` is reserved for the lead's cross-module PRs.
- `CODEOWNERS` is generated from the registry and checked for drift.
- One owner per module; reviewers are additional people, not second writers.
- WIP = 1; PRs under 400 changed lines; squash merge; no self-approval.

See `references/01-principles.md` for the full model.

## Scope and limits

- **GitHub-specific.** GitLab has CODEOWNERS and protected branches but different
  label/ruleset/project APIs; adapt `references/03` and keep the registry.
- **A label is a declaration, not a permission.** Anyone with Write can add
  `module:integration`; the lead's review is the control.
- **CODEOWNERS routes review; it does not limit scope.** The `modules` CI job does.
- **Private repositories on the free plan** may lack rulesets; use classic branch
  protection or treat the checks as advisory.
- **No secrets.** The registry and CODEOWNERS are public review metadata.
- **Not a build system.** The `test` job in `templates/ci.yml` is a placeholder;
  replace it with the project's own command.
- **Not a verifier.** The skill checks ownership and scope, not whether the code
  is correct; pair it with the project's tests and review.

## Repository layout

```text
SKILL.md              skill entry point (frontmatter + playbook)
README.md             this file
references/           six playbooks loaded on demand
scripts/              registry, generator, checker, label sync, validation, self-test
templates/            copyable project files
examples/example-project/   a four-module project used by the self-test
.github/              CI, CODEOWNERS, PR template
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Run the checks above before opening a
PR; keep changes focused; update `CHANGELOG.md` for user-visible changes.

## License

MIT. See [`LICENSE`](LICENSE).
