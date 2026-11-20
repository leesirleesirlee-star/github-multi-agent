# 01 - Principles

## Why module ownership

Parallel work fails in four predictable ways:

1. **Collisions** - two people edit the same file; the second merge loses work.
2. **Orphans** - a file has no owner, so nobody reviews it and it drifts.
3. **Review ambiguity** - a PR touches five areas and one reviewer approves all
   five without the context for any of them.
4. **Long branches** - a branch lives for two weeks, then conflicts with
   everything merged meanwhile.

A module registry plus a CI scope check addresses all four with one small
mechanism: ownership is explicit, checkable and visible before merge.

## The ten principles

1. **One writer per module.** Reviewers may be many; writers are one. Two writers
   on one module is the root of most conflicts.
2. **Explicit beats implicit.** If ownership is not in `modules.json` and
   `CODEOWNERS`, it does not exist. "Everyone knows Alice owns this" is not a
   control.
3. **Scope must be machine-checkable.** A rule that requires a human to notice a
   stray file is a hope. The CI scope check turns it into a red build.
4. **Small batches.** A PR under 400 lines is reviewable and revertible. A
   2,000-line PR is a merge conflict with a commit message.
5. **Contracts before parallel work.** Freeze the schema, API or corpus that two
   modules share. Parallel work on an unfrozen interface produces two
   incompatible guesses.
6. **Review independence.** The author of a change should not be the only person
   who signs its acceptance. The lead or a different module owner reviews.
7. **Evidence, not adjectives.** "Works", "fixed", "safe" are not states. Record
   the command, the observed output, the hash and the limitation.
8. **Freeze is a version, not a wall.** After a freeze, a change is a new version
   plus a decision record, not a silent edit.
9. **WIP = 1.** One in-progress issue per person. Multitasking across modules is
   how branches become stale.
10. **Handoff is a file.** A new person or agent should be able to start from a
    committed `START-HERE.md`, not from a chat scrollback.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| CODEOWNERS only | routes review, does not limit scope | add the CI module check |
| "Everyone owns docs" | no reviewer, no standard | one `docs` or `infra` owner |
| One `utils/` module | becomes a shared dumping ground | split by domain, or make the lead own it |
| Module per file | registry becomes noise | 4-8 modules for a small team |
| One long-lived branch | guaranteed conflicts | one issue, one short branch |
| Owner reviews own gate | circular evidence | lead or another owner signs |
| Optional module label | labels drift, checker cannot enforce | exactly one label, CI fails otherwise |
| Shared working tree | invisible concurrent edits | one clone/worktree per writer |
| "We'll add tests later" | the gate passes on nothing | tests live in the module's path |

## When not to use this

- A solo repository with no concurrent writers: CODEOWNERS is enough.
- A build system that already enforces ownership and you only need review
  routing: do not duplicate it.
- A repository where every change legitimately spans all modules: reduce to a
  smaller number of modules or use a single `integration` workflow instead.

## What success looks like

Measure after two weeks:

- unowned files: **0**
- PRs with a missing or duplicate module label: **0**
- median PR size: **under 400 lines**
- median review time: **under one working day**
- merge conflicts on `main`: **rare, and resolved by the owner**
- a new contributor can start from `START-HERE.md` without asking where to write

If the numbers are bad, do not add more rules. Reduce the number of modules,
shrink PRs, or fix the review bottleneck.

## Adoption path

1. Week 1: 4 modules, one owner each, CODEOWNERS, CI modules job, one negative
   test.
2. Week 2: add the project board, WIP limit, PR template, first gate.
3. Week 3: review the module boundaries; split a module only if it has two
   independent interfaces and two writers.
4. Never start with 12 modules. Start with the smallest map that gives each
   writer a clear home.
