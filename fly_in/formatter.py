class OutputFormatter:
    """Format simulation turns according to the Fly-in output specification."""

    def format_turn(self, moves: list[str]) -> str:
        """Format one simulation turn."""
        return " ".join(moves)

    def format(self, turns: list[list[str]]) -> str:
        """Format the complete simulation output."""
        return "\n".join(
            self.format_turn(moves)
            for moves in turns
            if moves
        )