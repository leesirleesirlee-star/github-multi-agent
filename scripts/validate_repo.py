#!/usr/bin/env python3
"""Validate this skill package: frontmatter, syntax, links and generated files.

Run from the repository root:
    python scripts/validate_repo.py
Exit codes: 0 OK, 1 validation error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

try:  # run as a script
    from module_registry import load_registry, render_codeowners, validate_registry
except ModuleNotFoundError:  # imported as a package
    from scripts.module_registry import (  # type: ignore[no-redef]
        load_registry,
        render_codeowners,
        validate_registry,
    )

ROOT = Path(__file__).resolve().parents[1]
SKILL_LIMIT = 8192
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_skill(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md: missing YAML frontmatter")
        return
    try:
        _, front, _ = text.split("---\n", 2)
    except ValueError:
        errors.append("SKILL.md: frontmatter is not closed")
        return
    meta = yaml.safe_load(front) or {}
    if meta.get("name") != "github-multi-agent":
        errors.append(f"SKILL.md: unexpected name {meta.get('name')!r}")
    if not meta.get("description"):
        errors.append("SKILL.md: description is required")
    if len(text) > SKILL_LIMIT:
        errors.append(f"SKILL.md: {len(text)} bytes exceeds {SKILL_LIMIT}")


def check_json_yaml(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - report every parse error
                errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        elif path.suffix in {".yml", ".yaml"}:
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - report every parse error
                errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")


def check_python(errors: list[str]) -> None:
    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: syntax error: {exc}")


def check_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK_RE.findall(line):
                target = target.strip()
                if not target or target.startswith(
                    ("#", "http://", "https://", "mailto:", "file:")
                ):
                    continue
                if urlparse(target).scheme:
                    continue
                rel = target.split("#", 1)[0]
                if rel and not (path.parent / rel).exists():
                    errors.append(
                        f"{path.relative_to(ROOT)}:{number}: missing link target {target!r}"
                    )


def check_generated(errors: list[str]) -> None:
    pairs = [
        (ROOT / "templates" / "modules.json", ROOT / "templates" / "CODEOWNERS"),
        (
            ROOT / "examples" / "example-project" / "modules.json",
            ROOT / "examples" / "example-project" / ".github" / "CODEOWNERS",
        ),
    ]
    for registry_path, output_path in pairs:
        registry = load_registry(registry_path)
        problems = validate_registry(registry)
        if problems:
            errors.extend(f"{registry_path.relative_to(ROOT)}: {p}" for p in problems)
            continue
        expected = render_codeowners(registry)
        actual = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        if actual != expected:
            errors.append(
                f"{output_path.relative_to(ROOT)}: stale; run "
                "python scripts/generate_codeowners.py"
            )


def main() -> int:
    errors: list[str] = []
    check_skill(errors)
    check_json_yaml(errors)
    check_python(errors)
    check_links(errors)
    check_generated(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("repo validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
