# START HERE - <project name>

**Status:** <milestone>, <date>. <what is done>. <what is not>.
**Repository:** <url>
**Owner / lead:** <@handle>

This is the onboarding file for a person or agent who opens this repository with
no history. Read it before changing anything.

## 1. What this project is

<One paragraph: the problem, the user, the output.>

**What it is not:** <scope limits and non-claims.>

## 2. The flow

```text
<input> -> <step 1> -> <step 2> -> <step 3> -> <output>
```

## 3. Read in this order

| # | Document | Why |
|---|---|---|
| 1 | `README.md` | one-page overview |
| 2 | `AGENTS.md` | binding rules for agents |
| 3 | `docs/plan/00-...` | scope and milestones |
| 4 | `modules.json` | module map and ownership |
| 5 | `docs/adr/` | decisions that changed the design |

## 4. What exists today

| Path | State | Owner |
|---|---|---|
| `<path>` | <written / skeleton / missing> | <@handle> |

## 5. Modules and owners

| Module | Owner | Paths | Gate |
|---|---|---|---|
| `contract` | <@handle> | `schemas/`, `docs/interfaces/` | M0 |
| `core` | <@handle> | `src/core/`, `tests/core/` | M1 |
| `ui` | <@handle> | `src/ui/`, `tests/ui/` | M2 |
| `infra` | <@handle> | `.github/`, `scripts/`, `docs/`, root files | M0 |

`modules.json` is the source of truth. A PR must carry exactly one
`module:<id>` label and must not change files outside that module.

## 6. The next 10 days

- [ ] <task, owner, exit condition>
- [ ] <task, owner, exit condition>
- [ ] <task, owner, exit condition>

## 7. Non-negotiable rules

1. One owner per module; do not edit another module's files.
2. One issue, one branch, one owner, one module label.
3. PRs under 400 changed lines; squash merge; delete the branch.
4. No secrets, credentials or private data in the repository.
5. <domain-specific safety rule>
6. A missing check is reported as missing, never as a pass.
7. Claims need a command, an observed result and a hash.

## 8. Glossary

| Term | Meaning |
|---|---|
| Module | one owner + one path scope + one interface + one gate |
| Integration PR | a cross-module PR labelled `module:integration` and reviewed by the lead |
| Freeze | an interface/corpus is fixed at a milestone; changes need a new version |
| WIP | work in progress; one per person |

## 9. Open decisions

- [ ] <decision the lead must make>
- [ ] <decision the lead must make>

## 10. Hand this folder to someone else

1. Clone the repository and open this file.
2. Read section 3 in order.
3. Run the checks and the negative test in `docs/workflow/`.
4. Pick an issue with one `module:<id>` label.
5. Branch `feat/<module>/<issue>-<slug>`, change only that module, open a PR with
   the same label.
6. Ask the module owner for review.
