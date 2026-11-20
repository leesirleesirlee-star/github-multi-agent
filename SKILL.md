---
name: github-multi-agent
description: Set up and run a multi-person or multi-agent GitHub repository with precise module ownership - a modules.json registry, generated CODEOWNERS, a CI scope check, branch protection, issue/PR templates, a project board, and handoff docs. Use when 2-10 people or agents share one repository and edits, reviews, or merges collide.
whenToUse: The user asks for a team GitHub workflow, CODEOWNERS, branch protection, module ownership, conflict prevention, or an onboarding/handoff process for a shared repository.
---

# GitHub multi-agent collaboration

Turn "several people, one repository" into a checkable process: every tracked
path belongs to exactly one module, every module has one owner, every PR
declares its module, and CI rejects changes outside it.

The same rules work for human teams and for AI agent teams. Agents are treated
like contributors with a write scope, not like free-form editors.

## When to use

- 2-10 contributors share one repository and step on each other.
- Reviewers cannot tell who owns a directory.
- PRs touch unrelated modules and conflict on `main`.
- You need a repeatable onboarding and merge process, not a one-off rule.

Do not use it for a solo repository with no parallel writers, or when an existing
build system already enforces ownership and you only need CODEOWNERS.

## What the skill provides

| Piece | File | Purpose |
|---|---|---|
| Module registry | `scripts/module_registry.py`, `modules.json` | one source of truth for owners, paths, dependencies, gates |
| CODEOWNERS generator | `scripts/generate_codeowners.py` | deterministic review routing, checked for drift in CI |
| Scope checker | `scripts/check_modules.py` | fails a PR whose files fall outside its declared module |
| Label sync | `scripts/sync_labels.py` | creates one `module:<id>` label per module from the registry |
| CI template | `templates/ci.yml` | `test`, `modules`, `codeowners` jobs |
| GitHub runbook | `references/03-github-setup.md` | labels, ruleset, project, first issues, negative test |
| PR/issue templates | `templates/` | module label, acceptance criteria, decision records |
| Handoff templates | `templates/START-HERE.md`, `AGENTS.template.md`, `MIGRATION.md` | onboarding for a new person or agent |
| Scaling playbook | `references/04-scaling-roles.md` | 2, 3, 5, 8, 10 contributors |
| Conflict playbook | `references/05-handoff-and-conflicts.md` | freeze, rework, escalation, shared files |

## The model

A **module** is one owner + one path scope + one public interface + one gate.

1. **One owner per module.** Other people may review, not edit. Co-owners are
   reviewers, not a second writer.
2. **Every tracked path belongs to exactly one module.** An unowned file fails
   CI; add it to `modules.json` or delete it.
3. **A PR declares exactly one `module:<id>` label.** Every changed file must
   belong to that module. Cross-module work is split, or uses
   `module:integration` with the lead's review.
4. **Contracts are modules too.** Schemas, public APIs and frozen artifacts have
   an owner and a version; they are not a shared scratch pad.
5. **Small PRs, short branches.** Target under 400 changed lines; one issue per
   branch; rebase daily; squash merge.
6. **WIP = 1.** One `In progress` issue per person. A second issue stays
   `Ready`.
7. **No self-approval.** The owner does not sign their own gate. The lead merges
   gate PRs.
8. **Freeze before parallel work.** Freeze interfaces and test corpora at a
   milestone; later changes need a new version and an ADR.
9. **Evidence in the PR.** Commands run, observed output, hashes, and known
   limitations. "It works" is not evidence.
10. **The repository is the message bus.** Chat may notify; decisions and
    handoffs live in issues, PRs, ADRs and committed docs.

## Quick start (15 minutes)

1. Copy `scripts/` into the project and add `modules.json` from
   `templates/modules.json`.
2. Edit the module ids, owners and paths. Start with 4-6 modules, not 15.
3. Generate and commit CODEOWNERS:
   ```bash
   python scripts/generate_codeowners.py
   python scripts/generate_codeowners.py --check
   ```
4. Run the self-test:
   ```bash
   python scripts/selftest.py
   ```
5. Add `templates/ci.yml` as `.github/workflows/ci.yml`; replace the `test` job's
   install/test commands with the project's own.
6. Protect `main`: one approval, code-owner review, `ci / test`,
   `ci / modules`, `ci / codeowners`, up to date, no force push.
7. Create one `module:<id>` label per module with
   `python scripts/sync_labels.py --apply` (or add them in the UI), and a Project
   field `Module`.
8. Write `START-HERE.md` from the template and replace the placeholders.
9. Run the negative test in `references/03-github-setup.md`: a file outside the
   declared module must fail `ci / modules`.

## Daily flow

```text
issue (one module label)
  -> branch feat/<module>/<issue>-<slug>
  -> change only that module
  -> PR with the same module label
  -> CI: test + modules + codeowners
  -> CODEOWNER review
  -> squash merge
  -> board moves to Done
```

If a task needs two modules, split it. If it genuinely cannot be split, the lead
labels it `module:integration`, explains why, and reviews it.

## Scaling in one table

| Team size | Module shape | Roles |
|---|---|---|
| 2-3 | 3-5 modules; one person may own two related modules | one lead/integration + owners |
| 4-6 | one module per person; contract and infra may share the lead | lead + owners + reviewers |
| 7-10 | split large modules; add reviewers; never split one module between two writers | lead + owners + reviewers + release manager |
| Agents | one agent per module; shared task board; write scopes recorded | lead agent + module agents |

More detail: `references/04-scaling-roles.md`.

## Conflict rules that actually prevent conflicts

- Do not edit a file you do not own; open an issue instead.
- One issue, one branch, one owner. Never share a branch.
- If two tasks need the same file, sequence them: the owner writes, the other
  rebases after the first merge.
- Shared files (`modules.json`, `CODEOWNERS`, root configs) have one owner; batch
  their changes into one PR.
- Freeze means freeze: after a milestone, a change is a new version and a new
  gate, not an edit.
- A failed PR returns to its owner, not to a new person.

## Verify that it works

Do not trust a workflow you have not tested negatively:

1. Change a file in module A, label the PR `module:B`.
2. `ci / modules` must fail with `outside module B: <path> -> A`.
3. Change the label to `module:A`; the job must pass.
4. Edit `.github/CODEOWNERS` by hand; `ci / codeowners` must fail.
5. Run `python scripts/generate_codeowners.py`; the job must pass.

If the negative test passes, the ruleset is real. If it does not, the ruleset is
decoration.

## References

- `references/01-principles.md` - why module ownership works, anti-patterns.
- `references/02-module-registry.md` - schema, matching algorithm, dependency
  rules, adding a module, failure messages.
- `references/03-github-setup.md` - labels, ruleset, project board, first issues,
  weekly rhythm.
- `references/04-scaling-roles.md` - 2-10 contributors and agent teams.
- `references/05-handoff-and-conflicts.md` - onboarding, migration, freeze,
  rework, escalation.
- `references/06-examples.md` - 2-person, 5-person and 8-person module maps.

## Templates and scripts

- `templates/modules.json` - a 5-module starting point.
- `templates/ci.yml` - `test`, `modules`, `codeowners` jobs.
- `templates/PULL_REQUEST_TEMPLATE.md`, `templates/ISSUE_TEMPLATE/` - issue/PR
  forms that ask for the module label.
- `templates/CONTRIBUTING.md` - branch, PR, review and evidence rules.
- `templates/START-HERE.md`, `templates/AGENTS.template.md`,
  `templates/MIGRATION.md` -
  onboarding and rewrite handoff.
- `scripts/selftest.py` - proves the registry, checker, generator and label sync
  work.
