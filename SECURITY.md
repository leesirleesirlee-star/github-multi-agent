# Security policy

## Supported versions

The current `main` branch and the latest release receive fixes. Older copies are
not maintained.

## Reporting

Do not open a public issue for a vulnerability. Use the repository's
**Security > Report a vulnerability** flow (GitHub private security advisory) so
the report and any fix can be coordinated before disclosure.

Include:

- the affected script or template;
- the command and input that reproduce the issue;
- the observed and expected behavior;
- the Python version and operating system.

Do not include a real token, key, private repository URL or client data. If a
credential may have been exposed, rotate it first.

## Scope

This repository contains review and CI helper scripts plus templates. It does not
run a service and does not process untrusted binaries. The relevant risks are:

- a script writing outside the repository (path traversal);
- a generated CODEOWNERS or registry rule granting unintended review scope;
- a template that encourages committing a secret;
- a malicious pull request modifying the validation scripts.

Review the diff of `scripts/` and `.github/` with the same care as the templates.

## Safe defaults

- The scripts read `modules.json`, a git diff and local files; they do not call a
  network service.
- `sync_labels.py` only calls `gh` when run with `--apply`; the default is a dry
  run that prints commands.
- No secret is required by the package. A project using it may have its own
  provider key; that key never belongs in this repository.

## Disclosure

After a fix is available, the maintainer publishes a short advisory and credits
the reporter unless they ask to remain anonymous.
