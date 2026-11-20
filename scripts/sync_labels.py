#!/usr/bin/env python3
"""Create one module:<id> label per module, plus the integration label.

Usage:
    python scripts/sync_labels.py            # print gh commands
    python scripts/sync_labels.py --apply    # run gh label create --force

Requires the GitHub CLI (``gh``) only for ``--apply``. The default is a dry run.
"""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

try:  # run as a script
    from module_registry import load_registry, validate_registry
except ModuleNotFoundError:  # imported as a package
    from scripts.module_registry import (  # type: ignore[no-redef]
        load_registry,
        validate_registry,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="project root (default: cwd)")
    parser.add_argument(
        "--registry", default=None, help="path to modules.json (default: <root>/modules.json)"
    )
    parser.add_argument("--color", default="ededed", help="label color (hex, no #)")
    parser.add_argument(
        "--apply", action="store_true", help="run gh instead of printing commands"
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
    registry = load_registry(registry_path.resolve())

    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"invalid modules.json: {error}", file=sys.stderr)
        return 2

    prefix = registry.module_label_prefix
    labels: list[tuple[str, str]] = [
        (f"{prefix}{module.id}", module.title) for module in registry.modules
    ]
    labels.append((registry.integration_label, "Cross-module integration PR"))

    if args.apply and shutil.which("gh") is None:
        print("gh is not on PATH; install GitHub CLI or run without --apply", file=sys.stderr)
        return 1

    for name, description in labels:
        command = [
            "gh",
            "label",
            "create",
            name,
            "--color",
            args.color,
            "--description",
            description[:100],
            "--force",
        ]
        if args.apply:
            subprocess.run(command, check=True)
        else:
            print(shlex.join(command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
