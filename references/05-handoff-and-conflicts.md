# 05 - Handoff, freeze and conflict protocol

## Onboarding: `START-HERE.md`

Every repository needs one file that a new person or agent reads first. It is not
a duplicate of the README; it is the **current state** and the next action.

Sections:

1. **Status** - milestone, date, what is done, what is not.
2. **What this project is / is not** - scope and non-claims.
3. **The flow** - a short diagram of the pipeline or product.
4. **Read in this order** - 5-9 documents, each with one line on why.
5. **What exists today** - a table of directories and their state.
6. **What is not here and where it lives** - archive, old repo, external docs.
7. **Modules and owners** - one table; link `modules.json`.
8. **The next 10 days** - a checklist with owners and exit criteria.
9. **Non-negotiable rules** - safety, evidence, review, secrets.
10. **Glossary** - only the terms a newcomer needs.
11. **Open decisions** - what the lead must confirm.
12. **How to hand this folder to someone else** - clone, read, run checks, pick
    an issue.

Keep it current. A stale `START-HERE.md` is worse than none: it sends a newcomer
to the wrong file.

## Migration: `MIGRATION.md`

When a project is rewritten or split, write a keep/import/drop manifest:

| Column | Meaning |
|---|---|
| Source path | where the file lives today |
| Destination | where it goes in the new tree |
| Action | copy, adapt, reference only, do not import |
| Owner | who imports it |
| Why | one sentence |

Rules:

- Copy documents and visual assets; do not copy an old architecture wholesale.
- Do not import old evidence as new evidence.
- Record the source commit and the SHA-256 of every imported file.
- Mark imported docs read-only; current docs win on conflict.
- Source separation: build-only sources never enter an analysis or prompt path.

## Conflict protocol

When two people need the same file:

1. **Stop.** Do not edit around the other person.
2. **Check ownership.** `modules.json` and CODEOWNERS say who writes.
3. **Open an issue** naming the file, both needs, and the proposed order.
4. **Sequence.** The owner writes first; the other rebases after the merge.
5. **Escalate** to the lead if the order is contested or the change crosses
   modules.

Do not resolve a conflict by copying the file into a second module. That creates
two sources of truth.

## Shared files

Some files are genuinely shared: `modules.json`, `CODEOWNERS`, root configs,
lockfiles, the top-level README. Give each one an owner, usually the lead.

- Batch shared-file changes into one PR.
- Do not reformat a shared file while changing one line.
- Announce a shared-file change in the issue that owns it.
- Generated files are changed by their generator, not by hand.

## Cross-module changes

A change that genuinely spans modules is an `integration` PR:

1. The lead applies `module:integration` and explains the coupling.
2. Every affected module owner reviews.
3. The PR includes a rollback note and the tests for each module.
4. If the coupling is recurring, fix the module boundaries instead of repeating
   the integration PR.

Routine work does not use `module:integration`. It is a signal, not a shortcut.

## Freeze protocol

Freeze an interface, schema, corpus or fixture at a milestone when parallel work
depends on it.

- A freeze is a tag/commit plus a note: what is frozen, who reviewed it, what is
  allowed to change.
- After the freeze, a change is a **new version** plus an ADR. The old version
  stays readable.
- A frozen artifact is not edited to make a test pass. If it is wrong, version it
  and re-run the gate.
- Announce the freeze in the project and the `START-HERE.md` status.

## Stale branches and PRs

- A branch older than five working days is suspect: rebase or close it.
- A PR with no review after two working days: the lead assigns a reviewer or
  closes it.
- A PR that conflicts with `main` is the author's job to rebase, not the
  reviewer's.
- Do not merge a stale branch "because it was almost done". Rebase and re-run the
  checks.

## Rework

- A failed PR returns to its owner.
- A failed gate returns to the module owner with the exact failing check and
  evidence.
- Do not reassign a failure to a new person to get a green result.
- If the check itself is wrong, change the check in an ADR with the lead; do not
  silently relax it.

## Decision records

Use a short ADR for:

- a contract or schema change;
- a module boundary change;
- a gate waiver;
- a tool or dependency that affects the whole team;
- a freeze or a version bump.

Format: context, options, decision, consequences, affected owners. Keep it in
`docs/adr/` and link it from the PR.

## Escalation

| Situation | Escalate to | Artifact |
|---|---|---|
| Two owners claim one file | lead | issue with both links |
| A gate fails and the cause is unclear | lead + module owner | failing command + output |
| A contract change is needed after freeze | lead + all consumers | ADR |
| A reviewer is unavailable | lead | PR comment naming the substitute |
| A secret or client data leaked | lead immediately | incident note; rotate first |
| Scope creep threatens the milestone | lead | issue with the cut list |

Escalation is not failure. Silent workarounds are.
