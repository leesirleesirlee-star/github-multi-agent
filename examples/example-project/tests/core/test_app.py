from src.core.app import run


def test_run() -> None:
    assert run("  A ") == "a"
