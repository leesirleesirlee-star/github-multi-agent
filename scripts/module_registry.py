"""Module registry helpers for a multi-person GitHub repository.

The registry is ``modules.json`` at the project root. It is the single source of
truth for module ownership, write scope, dependency direction and gates. The CI
scope check and the CODEOWNERS generator both use this module.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class Module:
    """One module: a write scope with one owner and a public interface."""

    id: str
    title: str
    owner: str
    reviewers: tuple[str, ...]
    paths: tuple[str, ...]
    may_depend_on: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    interfaces: tuple[str, ...]
    gate: str
    notes: str


@dataclass(frozen=True)
class Registry:
    """The parsed ``modules.json`` plus its global settings."""

    modules: tuple[Module, ...]
    default_reviewers: tuple[str, ...]
    ignored_prefixes: tuple[str, ...]
    module_label_prefix: str
    integration_label: str


def load_registry(path: Path) -> Registry:
    """Load and parse a module registry file."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    modules = tuple(
        Module(
            id=item["id"],
            title=item["title"],
            owner=item["owner"],
            reviewers=tuple(item.get("reviewers", ())),
            paths=tuple(item["paths"]),
            may_depend_on=tuple(item.get("may_depend_on", ())),
            forbidden_paths=tuple(item.get("forbidden_paths", ())),
            interfaces=tuple(item.get("interfaces", ())),
            gate=str(item.get("gate", "")),
            notes=item.get("notes", ""),
        )
        for item in raw["modules"]
    )
    return Registry(
        modules=modules,
        default_reviewers=tuple(raw.get("default_reviewers", ())),
        ignored_prefixes=tuple(raw.get("ignored_prefixes", ())),
        module_label_prefix=raw.get("module_label_prefix", "module:"),
        integration_label=raw.get("integration_label", "module:integration"),
    )


def normalize_path(path: str) -> str:
    """Normalize a repository-relative path to forward slashes."""

    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def is_ignored(path: str, registry: Registry) -> bool:
    """Return True for runtime or tooling paths that are not tracked."""

    normalized = normalize_path(path)
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in registry.ignored_prefixes
    )


def match_path(path: str, registry: Registry) -> Module | None:
    """Return the module that owns ``path``, or None if it is unowned.

    Exact file rules win over prefix rules; among prefixes, the longest one wins.
    A tie between two different modules is a registry bug and raises ValueError.
    """

    normalized = normalize_path(path)
    for module in registry.modules:
        for rule in module.paths:
            if not rule.endswith("/") and normalized == normalize_path(rule):
                return module

    best_length = -1
    best: Module | None = None
    for module in registry.modules:
        for rule in module.paths:
            if not rule.endswith("/"):
                continue
            prefix = normalize_path(rule)
            if not normalized.startswith(prefix):
                continue
            if len(prefix) > best_length:
                best_length = len(prefix)
                best = module
            elif len(prefix) == best_length and best is not None and best.id != module.id:
                raise ValueError(
                    f"ambiguous path {normalized!r}: {best.id} and {module.id} "
                    f"both claim prefix {prefix!r}"
                )
    return best


def classify(paths: list[str], registry: Registry) -> list[tuple[str, Module | None]]:
    """Classify each path, preserving input order."""

    return [(normalize_path(path), match_path(path, registry)) for path in paths]


def _is_handle(value: str) -> bool:
    return value.startswith("@") and len(value) > 1


def _validate_path_rule(rule: str) -> str | None:
    normalized = normalize_path(rule)
    if not normalized:
        return "empty path rule"
    if Path(normalized).is_absolute() or normalized.startswith("/"):
        return f"path must be repository-relative: {rule!r}"
    if ".." in Path(normalized).parts:
        return f"path must not contain '..': {rule!r}"
    if normalized.endswith("/") and "\\" in rule:
        return f"use '/' in path rules: {rule!r}"
    return None


def validate_registry(registry: Registry) -> list[str]:
    """Return structural errors; an empty list means the registry is valid."""

    errors: list[str] = []
    if not registry.modules:
        errors.append("modules must not be empty")
    ids = [module.id for module in registry.modules]
    if len(ids) != len(set(ids)):
        errors.append("duplicate module id")
    for reviewer in registry.default_reviewers:
        if not _is_handle(reviewer):
            errors.append(f"default_reviewers: invalid handle {reviewer!r}")
    if not registry.module_label_prefix.endswith(":"):
        errors.append("module_label_prefix must end with ':'")
    if not registry.integration_label.startswith(registry.module_label_prefix):
        errors.append("integration_label must start with module_label_prefix")

    for module in registry.modules:
        if not ID_RE.match(module.id):
            errors.append(f"{module.id!r}: id must be kebab-case")
        if module.id == "integration":
            errors.append(
                "module id 'integration' is reserved for the integration label"
            )
        if not module.title.strip():
            errors.append(f"{module.id}: empty title")
        if not _is_handle(module.owner):
            errors.append(f"{module.id}: owner must be a GitHub handle like @name")
        for reviewer in module.reviewers:
            if not _is_handle(reviewer):
                errors.append(f"{module.id}: invalid reviewer {reviewer!r}")
        if not module.paths:
            errors.append(f"{module.id}: empty paths list")
        for rule in module.paths:
            problem = _validate_path_rule(rule)
            if problem:
                errors.append(f"{module.id}: {problem}")
        for dependency in module.may_depend_on:
            if dependency not in ids:
                errors.append(f"{module.id}: unknown dependency {dependency!r}")
            if dependency == module.id:
                errors.append(f"{module.id}: depends on itself")

    exact_paths: dict[str, str] = {}
    for module in registry.modules:
        for rule in module.paths:
            if not rule.endswith("/"):
                key = normalize_path(rule)
                if key in exact_paths and exact_paths[key] != module.id:
                    errors.append(
                        f"{key!r} is claimed by both {exact_paths[key]} and {module.id}"
                    )
                exact_paths[key] = module.id
    return errors


def render_codeowners(registry: Registry) -> str:
    """Render a deterministic CODEOWNERS file from the registry.

    The default rule comes first, then path rules sorted shortest-first so the
    last matching rule is the most specific. Exact file rules sort after the
    directory rule with the same length.
    """

    lines = [
        "# Generated by scripts/generate_codeowners.py from modules.json.",
        "# Do not edit by hand; edit modules.json and regenerate.",
    ]
    default = " ".join(registry.default_reviewers)
    if default:
        lines.append(f"* {default}")

    rules: list[tuple[int, int, str, str]] = []
    for module in registry.modules:
        reviewers = " ".join((module.owner, *module.reviewers)).strip()
        for path in module.paths:
            clean = normalize_path(path)
            rules.append(
                (len(clean), 0 if clean.endswith("/") else 1, clean, reviewers)
            )
    for _, _, path, reviewers in sorted(rules):
        lines.append(f"{path} {reviewers}")
    return "\n".join(lines) + "\n"


def changed_files(base: str, root: Path) -> list[str]:
    """Return files changed between ``base`` and HEAD.

    Raises RuntimeError when git fails, for example because the base ref was not
    fetched in CI.
    """

    command = ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"]
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git diff failed"
        raise RuntimeError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
