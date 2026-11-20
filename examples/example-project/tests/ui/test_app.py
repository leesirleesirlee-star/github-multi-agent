from src.ui.app import render


def test_render() -> None:
    assert render("a") == "[a]"
