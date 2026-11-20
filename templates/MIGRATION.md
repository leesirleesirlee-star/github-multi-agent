# MIGRATION - <old project> to <new project>

**Source:** <repo/path, tag or commit>
**Target:** <repo/path>
**Owner:** <@handle>

## Principle

Copy documents and visual assets deliberately. Do not copy the old application
architecture, old evidence or old acceptance claims wholesale.

## Keep / import / drop

| Category | Source path | Destination | Action | Owner | Why |
|---|---|---|---|---|---|
| Onboarding | `<path>` | `START-HERE.md` | rewrite | <@handle> | new status |
| Product docs | `<path>` | `docs/archive/<version>/` | copy | <@handle> | rationale |
| Visual assets | `<path>` | `src/ui/` | adapt | <@handle> | reuse the look |
| Transport/client | `<path>` | `src/core/transport/` | adapt | <@handle> | reusable |
| Old evidence | `<path>` | none | do not import | - | binds to the old result |
| Old routes/workers | `<path>` | none | do not import | - | different architecture |

## Import procedure

1. Take bytes from a tag or commit, not a working tree.
2. Record source repo, commit, source path, destination and SHA-256 in
   `docs/archive/<version>/IMPORT.md`.
3. Do not edit imported bytes; adapt a copy in the owning module.
4. Run `python scripts/check_modules.py --base origin/main`.
5. Do not cite an old verdict as new evidence.

## Source separation

- <build-only directory> must never be read by analysis or prompt code.
- A test asserts the prompt contains no source path or source text.
- Client binaries, keys and private logs never cross the boundary.

## Checklist

- [ ] The new project can be explained without the old repository.
- [ ] Every imported file has a source commit and hash.
- [ ] Current docs win on conflict with archive docs.
- [ ] Old evidence is not cited as new evidence.
- [ ] The module registry covers every imported path.
