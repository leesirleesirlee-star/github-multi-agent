# 03 - GitHub setup runbook

**Run once as the lead, then keep it as the reference for new projects.**

## 0. Prerequisites

- The repository exists and the skeleton (including `modules.json`,
  `scripts/`, `.github/CODEOWNERS`) is on `main`.
- The lead has Admin; the other contributors have Write.
- `gh` CLI is optional. Every step has a UI equivalent.

## 1. Repository settings

| Setting | Value |
|---|---|
| Description | one sentence: what the project does |
| Topics | language, domain, `team-workflow` |
| Default branch | `main` |
| License | choose one; the lead commits it |
| Features | Issues on, Projects on, Wiki off unless used, Discussions off unless used |
| Merge | Allow squash merge only; disable merge commit and rebase merge |
| Auto-delete head branches | On |
| Secrets | none for the basic workflow; add only what CI genuinely needs |

## 2. Collaborators and teams

- Invite every contributor with **Write**.
- Keep Admin on the lead (and one backup).
- If the repository is under an organization, create a team per large area and
  reference `@org/team` in `modules.json`; otherwise use individual handles.
- Protect the lead account with 2FA. A shared account is a shared audit trail.

## 3. Labels

Create one `module:<id>` label per module, plus type, priority and status labels.

Type, priority and status labels with GitHub CLI:

```bash
gh label create "type:feat"       --color a2eeef --force
gh label create "type:fix"        --color d73a4a --force
gh label create "type:docs"       --color 0075ca --force
gh label create "type:test"       --color bfd4f2 --force
gh label create "type:decision"   --color c5def5 --force
gh label create "priority:P0"     --color b60205 --force
gh label create "priority:P1"     --color d93f0b --force
gh label create "priority:P2"     --color fbca04 --force
gh label create "status:blocked"  --color 000000 --force
```

Generate the module labels from the registry so they cannot drift:

```bash
python scripts/sync_labels.py            # dry run: print gh commands
python scripts/sync_labels.py --apply    # create/update labels with gh
```

The script creates one `module:<id>` per module plus `module:integration`. It does
not create the type, priority or status labels; add those from the list above.
The exact colors do not matter; the names do.

## 4. Milestones

Create 3-5 milestones, not one per task. Example:

```bash
gh api repos/OWNER/REPO/milestones -f title="M0 bootstrap" -f due_on="2026-01-15T00:00:00Z"
gh api repos/OWNER/REPO/milestones -f title="M1 core"      -f due_on="2026-02-01T00:00:00Z"
gh api repos/OWNER/REPO/milestones -f title="M2 release"   -f due_on="2026-02-15T00:00:00Z"
```

A milestone is a gate, not a wish. Give it an exit condition in the project
description.

## 5. Protect `main`

Use **Settings > Rules > Rulesets > New branch ruleset** (public repositories on
the free plan; private repositories may need a paid plan, otherwise use classic
branch protection with the same values).

- Target: `main`.
- Enforce for administrators: on.
- Require a pull request before merging:
  - required approvals: **1**;
  - dismiss stale approvals: on;
  - require review from Code Owners: on;
  - require conversation resolution: on.
- Require status checks: `ci / test`, `ci / modules`, `ci / codeowners`;
  require the branch to be up to date.
- Block force pushes; restrict deletions.
- Allow squash merge only.

The checks appear only after the first PR runs. Enable the ruleset after the
skeleton push and before the first real feature PR.

Screenshot the ruleset into `docs/workflow/` and link it from `START-HERE.md` so
the control is auditable.

## 6. Project board

Create one project with:

- **Views:** Board (Backlog / Ready / In progress / In review / Blocked / Done),
  Table (all fields), Roadmap by milestone.
- **Fields:** Owner (person), Module (single-select, same ids as the labels),
  Milestone/Gate, Priority (P0/P1/P2), Depends on.
- **WIP limit:** one `In progress` card per person. A second card is `Ready`, not
  started.
- **Rule:** every issue and PR has exactly one `module:<id>` label; the card
  shows the same module.
- **Automation:** PR opened -> `In review`; PR merged -> `Done`.

The module field is the fastest way to answer "what is Alice doing" and "what is
blocked in core" without reading every issue.

## 7. First issues

Create a starter set, one per module plus the workflow itself:

| Title | Module | Owner | Exit |
|---|---|---|---|
| Bootstrap the repository and ruleset | `infra` | lead | protected `main`, CI green |
| Freeze the public contract | `contract` | lead | schema v0 committed |
| Build the core skeleton | `core` | owner | first PR merged |
| Build the UI shell | `ui` | owner | first screen renders |
| Add the CI module check | `infra` | lead | negative test fails as expected |
| Write `START-HERE.md` | `infra` | lead | a new person can start |

Do not create 30 issues. Create 6-8, one per module and one per gate.

## 8. Negative test (do not skip)

1. Branch `test/module-check`.
2. Change a file in module A, for example `src/core/app.py`.
3. Open a PR labelled `module:ui`.
4. `ci / modules` must fail:
   `outside module ui: src/core/app.py -> core`.
5. Change the label to `module:core`; the job must pass.
6. Edit `.github/CODEOWNERS` by hand; `ci / codeowners` must fail.
7. Run `python scripts/generate_codeowners.py`; the job must pass.
8. Close the test PR or merge it if the change is real.

If step 4 does not fail, the ruleset is decoration. Fix it before inviting the
team.

## 9. Weekly rhythm

| When | What | Who |
|---|---|---|
| Monday 30 min | Pick one issue per person; update the board; confirm the gate | lead |
| Daily async | PR and issue updates; no status-only chat | all |
| Wednesday 15 min | Blockers only; name the missing artifact | all |
| Friday 30 min | Demo; merge gate PRs; record the result | lead |
| Before a milestone | Re-run the gate command; write the dated record | lead |

## 10. Scaling the setup

| Team size | Extra setup |
|---|---|
| 2-3 | one `default_reviewers`; each person may own two related modules |
| 4-6 | one module per person; lead owns `contract` + `infra` |
| 7-10 | add a release manager; use a team handle for the default reviewer; split only modules with two independent interfaces |
| Agents | one agent per module; shared task board; record write scopes; no two agents on one module |

## Known limits

- CODEOWNERS does not limit the PR's scope; the `modules` job does.
- GitHub labels are editable by anyone with Write. The lead reviews
  `module:integration` PRs; the label is a declaration, not a permission.
- A private repository on the free plan may not have rulesets. Use classic branch
  protection, or accept that the CI checks are advisory and enforce the merge
  policy socially.
- The module job needs `fetch-depth: 0` and a fetched base branch. Without it,
  `git diff` fails; the job must fail, not pass.
