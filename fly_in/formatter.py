"""Output Formatter: format simulation turns into the required output text."""


class OutputFormatter:
    """Format simulation turns according to the Fly-in output specification."""

    def format_turn(self, moves: list[str]) -> str:
        """Format a single simulation turn

        into a space-separated string of moves.
        """
        return " ".join(moves)

    def format(self, turns: list[list[str]]) -> str:
        """Format the complete simulation output.

            Omit turns with no moves to match the required output.
            """
        return "\n".join(
                self.format_turn(moves) for moves in turns if moves
            )
