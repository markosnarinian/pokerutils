"""A panel with a form for entering odds against and outs, and grading the answer."""

from __future__ import annotations

import math

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical
from textual.widgets import Button, Input, Label, Static

from ..utils.poker import Draw

ODDS_TOLERANCE = 0.1


def parse_ratio(raw: str) -> float | None:
    """Parse "4.2" or "4.2:1" into a float, or None if it isn't a usable ratio."""
    parts = raw.split(":")
    if len(parts) > 2:
        return None
    try:
        value = float(parts[0]) / (float(parts[1]) if len(parts) == 2 else 1)
    except (ValueError, ZeroDivisionError):
        return None
    return value if math.isfinite(value) else None


class AnswerPanel(Vertical):
    """A form, next to the player's hand, for entering odds against and outs."""

    def __init__(self) -> None:
        super().__init__()
        self.expected: Draw | None = None

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Label(
                "Odds against:",
            )
            yield Input(placeholder="e.g. 4:1", id="odds-against", compact=True)
        with HorizontalGroup():
            yield Label("Outs:")
            yield Input(placeholder="e.g. 9", id="outs", compact=True)
        yield Button("Submit", id="submit")
        yield Static(id="answer-feedback", markup=False)

    def set_expected(self, draw: Draw | None) -> None:
        """Set the draw to grade against, and clear any previous answer."""
        self.expected = draw
        for field in ("odds-against", "outs"):
            self.query_one(f"#{field}", Input).value = ""
        self.query_one("#answer-feedback", Static).update("")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.grade()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.grade()

    def grade(self) -> None:
        """Compare the entered outs and odds against the current draw."""
        feedback = self.query_one("#answer-feedback", Static)
        if self.expected is None:
            feedback.update("No direct draw to price on this board.")
            return

        lines = []
        raw_outs = self.query_one("#outs", Input).value.strip()
        if not raw_outs:
            lines.append(f"Outs: {self.expected.outs} · Answer")
        elif raw_outs.isdigit() and int(raw_outs) == self.expected.outs:
            lines.append(f"Outs: {self.expected.outs} · Correct")
        else:
            lines.append(f"Outs: {self.expected.outs} · Try again")

        odds = self.expected.odds_against
        raw_odds = self.query_one("#odds-against", Input).value.strip()
        expected_odds = "--" if odds is None or odds == math.inf else f"{odds:.1f}:1"
        if not raw_odds:
            lines.append(f"Odds against: {expected_odds} · Answer")
        else:
            answer = parse_ratio(raw_odds)
            correct = (
                answer is not None
                and odds is not None
                and odds != math.inf
                and abs(answer - odds) <= ODDS_TOLERANCE
            )
            if answer is None:
                lines.append(f"Odds against: {expected_odds} · Invalid number")
            else:
                lines.append(
                    f"Odds against: {expected_odds} · {'Correct' if correct else 'Try again'}"
                )

        lines.append(f"{self.expected.name}, on the next card.")
        feedback.update("\n".join(lines))
