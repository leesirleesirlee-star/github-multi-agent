#!/usr/bin/env python3
"""Self-test for the generic module registry, checker and CODEOWNERS generator.

Run from the skill directory:
    python scripts/selftest.py
No third-party dependency is required.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

try:  # run as a script
    import check_modules
    import generate_codeowners
    import sync_labels
    from module_registry import (
        load_registry,
        match_path,
        render_codeowners,
        validate_registry,
    )
except ModuleNotFoundError:  # imported as a package
    from scripts import check_modules, generate_codeowners, sync_labels  # type: ignore[no-redef]
    from scripts.module_registry import (  # type: ignore[no-redef]
        load_registry,
        match_path,
        render_codeowners,
        validate_registry,
    )

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "example-project"


def run_check(root: Path, *args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = check_modules.main(["--root", str(root), *args])
    return code, out.getvalue(), err.getvalue()


def main() -> int:
    registry = load_registry(EXAMPLE / "modules.json")
    errors = validate_registry(registry)
    assert errors == [], errors

    assert match_path("src/core/app.py", registry).id == "core"
    assert match_path("src/ui/app.py", registry).id == "ui"
    assert match_path("docs/README.md", registry).id == "infra"
    assert match_path("docs/interfaces/README.md", registry).id == "contract"
    assert match_path("README.md", registry).id == "infra"
    assert match_path("unknown.txt", registry) is None

    codeowners = render_codeowners(registry)
    lines = codeowners.splitlines()
    assert lines[2] == "* @lead", lines
    assert "src/core/ @alice @bob" in lines
    assert "README.md @lead" in lines
    # The exact-file rule must come after a same-length directory rule.
    assert lines.index("README.md @lead") > lines.index("src/core/ @alice @bob")

    code, out, err = run_check(
        EXAMPLE, "--files", "src/core/app.py", "--labels", "module:core"
    )
    assert code == 0, (code, out, err)
    code, _, err = run_check(
        EXAMPLE,
        "--files",
        "src/core/app.py",
        "src/ui/app.py",
        "--labels",
        "module:core",
    )
    assert code == 1 and "outside module core" in err, (code, err)
    code, _, err = run_check(EXAMPLE, "--files", "unknown.txt")
    assert code == 1 and "unowned: unknown.txt" in err, (code, err)
    code, _, err = run_check(EXAMPLE, "--files", "src/core/app.py", "--labels", "")
    assert code == 1 and "exactly one module:" in err, (code, err)
    code, _, err = run_check(
        EXAMPLE,
        "--files",
        "src/core/app.py",
        "src/ui/app.py",
        "--labels",
        "module:integration",
    )
    assert code == 0, (code, err)
    code, _, err = run_check(EXAMPLE, "--files", "var/cache.bin")
    assert code == 0, (code, err)  # ignored prefix -> no files -> 0

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert generate_codeowners.main(["--root", str(EXAMPLE), "--check"]) == 0
    assert "in sync" in out.getvalue()

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert generate_codeowners.main(["--root", str(EXAMPLE), "--stdout"]) == 0
    assert "src/core/ @alice @bob" in out.getvalue()

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert sync_labels.main(["--root", str(EXAMPLE)]) == 0
    labels = out.getvalue()
    assert "module:core" in labels
    assert "module:integration" in labels

    print("selftest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
