# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-20

### Added

- `modules.json` registry with owner, reviewers, paths, dependencies and gates.
- Deterministic `CODEOWNERS` generator with a `--check` drift mode.
- CI scope checker: one `module:<id>` label per PR, every changed file must match.
- `sync_labels.py` for creating module labels from the registry.
- `validate_repo.py` for frontmatter, JSON/YAML syntax, Markdown links and
  generated-file checks.
- `selftest.py` with no third-party dependency.
- Six reference playbooks: principles, registry, GitHub setup, scaling, handoff
  and conflicts, worked examples.
- Project templates: `modules.json`, `ci.yml`, PR/issue forms, `START-HERE.md`,
  `AGENTS.template.md`, `MIGRATION.md`, `CONTRIBUTING.md`.
- A four-module example project used by the self-test.
- GitHub Actions CI and MIT license.

[0.1.0]: https://github.com/leesirleesirlee-star/github-multi-agent/releases/tag/v0.1.0
