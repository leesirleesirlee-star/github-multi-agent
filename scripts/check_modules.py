#!/usr/bin/env python3
"""Check changed files against modules.json and the PR module label.

Usage:
    python scripts/check_modules.py --base origin/main
    python scripts/check_modules.py --base origin/main --labels "module:core,type:feat"
    python scripts/check_modules.py --files src/core/a.py src/ui/b.ts

Exit codes:
    0  every changed file belongs to a module and the label matches (if checked)
    1  an ownership, scope or label error
    2  modules.json itself is invalid
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:  # run as a script (scripts/ on sys.path)
    from module_registry import (
        changed_files,
        is_ignored,
        load_registry,
        match_path,
        normalize_path,
        validate_registry,
    )
except ModuleNotFoundError:  # imported as a package
    from scripts.module_registry import (  # type: ignore[no-redef]
        changed_files,
        is_ignored,
        load_registry,
        match_path,
        normalize_path,
        validate_registry,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="origin/main",
        help="git ref to diff against (default: origin/main)",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="explicit file list; skips git diff (used by tests)",
    )
    parser.add_argument(
        "--labels",
        default=None,
        help="comma-separated PR labels; exactly one module:<id> label is required",
    )
    parser.add_argument(
        "--registry",
        default=None,
        help="path to modules.json (default: <root>/modules.json)",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="project root for git operations and the default registry",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable report instead of a table",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path.cwd().resolve()
    if args.registry:
        registry_path = Path(args.registry)
        if not registry_path.is_absolute():
            registry_path = root / registry_path
    else:
        registry_path = root / "modules.json"
    registry_path = registry_path.resolve()
    registry = load_registry(registry_path)

    structural_errors = validate_registry(registry)
    if structural_errors:
        for error in structural_errors:
            print(f"invalid modules.json: {error}", file=sys.stderr)
        return 2

    if args.files is None:
        try:
            files = changed_files(args.base, root)
        except RuntimeError as exc:
            print(f"git diff failed: {exc}", file=sys.stderr)
            return 1
    else:
        files = list(args.files)
    files = [normalize_path(path) for path in files if not is_ignored(path, registry)]

    if not files:
        print("no changed files to check")
        return 0

    errors: list[str] = []
    rows: list[dict[str, str | None]] = []
    touched: set[str] = set()

    for path in files:
        module = match_path(path, registry)
        if module is None:
            rows.append({"path": path, "module": None, "owner": None})
            errors.append(f"unowned: {path} (add it to a module in modules.json)")
            continue
        rows.append({"path": path, "module": module.id, "owner": module.owner})
        touched.add(module.id)

    declared: str | None = None
    if args.labels is not None:
        prefix = registry.module_label_prefix
        module_labels = [
            label.strip()
            for label in args.labels.split(",")
            if label.strip().startswith(prefix)
        ]
        if len(module_labels) != 1:
            errors.append(
                f"exactly one {prefix}<id> label is required; found {module_labels or 'none'}"
            )
        else:
            declared = module_labels[0][len(prefix) :]
            known = {module.id for module in registry.modules}
            if declared != "integration" and declared not in known:
                errors.append(f"unknown module label: {module_labels[0]}")
            elif declared != "integration":
                for row in rows:
                    if row["module"] is not None and row["module"] != declared:
                        errors.append(
                            f"outside module {declared}: {row['path']} -> {row['module']}"
                        )
                if declared not in touched:
                    errors.append(
                        f"declared module {declared} but no changed file belongs to it"
                    )

    if args.json:
        print(
            json.dumps(
                {
                    "base": args.base,
                    "declared_module": declared,
                    "touched_modules": sorted(touched),
                    "files": rows,
                    "errors": errors,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        width = max(len(row["path"]) for row in rows)
        print(f"{'file'.ljust(width)}  module / owner")
        print(f"{'-' * width}  --------------")
        for row in rows:
            if row["module"] is None:
                print(f"{row['path'].ljust(width)}  UNOWNED")
            else:
                print(f"{row['path'].ljust(width)}  {row['module']} / {row['owner']}")
        print()
        print(f"touched modules: {', '.join(sorted(touched)) or 'none'}")
        if declared:
            print(f"declared module: {declared}")
        if errors:
            print()
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
        else:
            print("OK: every changed file matches the declared module")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
