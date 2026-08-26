from fly_in.formatter import OutputFormatter


def test_format_turn() -> None:
    formatter = OutputFormatter()

    assert formatter.format_turn(
        ["D1-A", "D2-B"]
    ) == "D1-A D2-B"


def test_format_simulation() -> None:
    formatter = OutputFormatter()

    turns = [
        ["D1-A"],
        ["D1-B", "D2-A"],
        ["D1-C"],
    ]

    assert formatter.format(turns) == (
        "D1-A\n"
        "D1-B D2-A\n"
        "D1-C"
    )


def test_empty_turns_are_omitted() -> None:
    formatter = OutputFormatter()

    turns = [
        ["D1-A"],
        [],
        ["D1-B"],
    ]

    assert formatter.format(turns) == (
        "D1-A\n"
        "D1-B"
    )