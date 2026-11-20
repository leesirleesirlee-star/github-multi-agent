#!/usr/bin/env python3
"""Generate or verify .github/CODEOWNERS from modules.json.

Usage:
    python scripts/generate_codeowners.py
    python scripts/generate_codeowners.py --check
    python scripts/generate_codeowners.py --stdout

The generated file is deterministic: edit modules.json, not CODEOWNERS.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

try:  # run as a script
    from module_registry import load_registry, render_codeowners, validate_registry
except ModuleNotFoundError:  # imported as a package
    from scripts.module_registry import (  # type: ignore[no-redef]
        load_registry,
        render_codeowners,
        validate_registry,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="project root (default: cwd)")
    parser.add_argument(
        "--registry", default=None, help="path to modules.json (default: <root>/modules.json)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="CODEOWNERS path (default: <root>/.github/CODEOWNERS)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if the file is stale")
    mode.add_argument("--stdout", action="store_true", help="print instead of writing")
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

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
    else:
        output_path = root / ".github" / "CODEOWNERS"
    output_path = output_path.resolve()

    registry = load_registry(registry_path)
    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"invalid modules.json: {error}", file=sys.stderr)
        return 2

    rendered = render_codeowners(registry)

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        existing = (
            output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        )
        if existing == rendered:
            print(f"in sync: {output_path}")
            return 0
        print(f"stale: {output_path}", file=sys.stderr)
        diff = difflib.unified_diff(
            existing.splitlines(),
            rendered.splitlines(),
            fromfile=str(output_path),
            tofile="generated",
            lineterm="",
        )
        for line in list(diff)[:40]:
            print(line, file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
