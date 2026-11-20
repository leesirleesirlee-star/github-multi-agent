# 04 - Scaling roles from 2 to 10 people

## Roles

| Role | Owns | Does not |
|---|---|---|
| **Lead / integration** | `modules.json`, `CODEOWNERS`, CI, branch protection, release, final merge, gate records | write every module; review their own work |
| **Module owner** | one module's paths, tests, interface, docs | edit another module; sign their own gate |
| **Reviewer** | a second pair of eyes on a module or gate | become a second writer |
| **Release manager** | tags, release notes, artifact hashes | change code at release time |
| **Contributor** | one issue in one module | push to `main`; touch unowned files |
| **Agent** | the same as a contributor, with a recorded write scope | act outside its module; merge its own PR |

The lead is a role, not a rank. On a two-person team one person may be lead and
also own `contract` + `infra`; the other owns the product modules.

## Team-size patterns

### 2 people

```text
A: contract + core + infra   (lead)
B: ui + tests + docs
```

- 3-4 modules is enough.
- `default_reviewers`: both handles, so either can approve the other.
- The lead owns the rules; the other owns the product surface.
- Do not create a module that neither person writes.

### 3 people

```text
A: contract + infra (lead)
B: core
C: ui + api
```

- Each person has one primary module and at most one secondary.
- `contract` stays with the lead; it is the shared interface.
- The reviewer is the next person, not the author.

### 5 people

```text
A: contract + infra (lead)
B: core
C: api
D: ui
E: tests + release
```

- One module per person, except the lead who owns the two small shared modules.
- If tests are written by each owner, drop the separate `tests` module and put
  tests under the owning module's path.
- The lead merges gate PRs; module owners merge their own after review.

### 8 people

```text
A: contract + infra (lead)
B: core-domain
C: core-runtime
D: api-public
E: api-internal
F: ui-web
G: ui-mobile
H: release + verification
```

- Split a module only when it has **two independent interfaces** and **two
  writers**.
- Add reviewers: each module has an owner plus one reviewer from a neighboring
  module.
- The release/verification person does not write the modules they verify.

### 10 people

- 8-10 modules is the practical maximum for a small project.
- Add a `platform`/`infra` module for CI, scripts and docs; do not let it become
  the dumping ground.
- Use a team handle (`@org/team`) for `default_reviewers` so the lead can rotate.
- Add a weekly integration review: the lead + two owners, 30 minutes.

## Module count heuristic

- **2-3 people:** 3-5 modules.
- **4-6 people:** 5-7 modules.
- **7-10 people:** 7-10 modules.
- One person should own **at most two** modules.
- If a module has no active writer for a milestone, merge it into a neighbor.

## Agent teams

The same rules apply, with three additions:

1. **One agent per module.** Two agents writing one module is the same collision
   as two people.
2. **Record the write scope.** A shared task board entry states the module, the
   files, the artifact and the acceptance check. An agent that needs another
   module sends a handoff, not a patch.
3. **The lead agent reviews.** An agent does not approve its own PR or write the
   final verdict for its own change.

Useful agent split:

```text
lead agent       contract, infra, merge, gate records
fixture agent    test data, corpus, build recipe
analysis agent   parsing, reports
repair agent     implementation
ui agent         screens, templates, rendering
```

If an agent is idle, do not give it another module's files. Give it a review, a
test, or a documentation task inside its own module.

## Ownership transfer

When an owner leaves or rotates:

1. Update `modules.json` owner (and `CODEOWNERS` via the generator).
2. Transfer open issues and the project card.
3. The old owner writes a one-page handoff: paths, interfaces, open decisions,
   known traps.
4. The new owner runs the module's checks and the negative test once.
5. Record the transfer in an ADR or the project log.

Do not leave a module with a "temporary" owner who never reviews. That is an
orphan with a name.

## Reviewer rotation

- Every module needs a named reviewer in addition to the owner.
- The reviewer must be able to run the module's checks.
- Rotate reviewers at each milestone; this spreads context and reduces bus
  factor.
- If the reviewer is unavailable, the lead substitutes and records it in the PR.

## Bus factor

A module is a bus-factor risk if only one person can build, test and explain it.
Mitigate with:

- a `README.md` in the module (inputs, outputs, commands);
- a failing test that demonstrates the contract;
- one review per milestone by a second person;
- a short handoff when the owner changes.

## Same-person limitation

On a small team, the lead may also be the verifier. Record it:

> The lead and the verifier are the same person; this is role separation, not
> independent two-person review.

Do not claim independent verification you did not have. The mitigation is a
second reviewer, a re-run by another owner, or a recorded limitation.
