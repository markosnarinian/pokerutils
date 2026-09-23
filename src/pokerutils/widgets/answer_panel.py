"""A panel with a form for entering odds against and outs, and grading the answer."""

from __future__ import annotations

import math

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical
from textual.widgets import Button, Input, Label, Static


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
        self.expected_outs: int | None = None
        self.expected_odds: float | None = None

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Label("Outs:", classes="answer-label")
            yield Input(placeholder="e.g. 9", id="outs", compact=True)
            yield Static(id="outs-result", classes="answer-result", markup=False)
        with HorizontalGroup():
            yield Label("Odds against:", classes="answer-label")
            yield Input(placeholder="e.g. 4:1", id="odds-against", compact=True)
            yield Static(id="odds-result", classes="answer-result", markup=False)
        yield Button("Submit", id="submit")

    def set_expected(self, outs: int | None, odds_against: float | None) -> None:
        """Set the overall result to grade against, and clear any previous answer."""
        self.expected_outs = outs
        self.expected_odds = odds_against
        for field in ("odds-against", "outs"):
            self.query_one(f"#{field}", Input).value = ""
        for result in ("outs-result", "odds-result"):
            self.query_one(f"#{result}", Static).update("")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.grade()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.grade()

    def grade(self) -> None:
        """Show each correct result alongside the entered value and its errors."""
        if not self.expected_outs or self.expected_odds is None:
            message = "No direct draw"
            self.query_one("#outs-result", Static).update(message)
            self.query_one("#odds-result", Static).update(message)
            return

        raw_outs = self.query_one("#outs", Input).value.strip()
        entered_outs = int(raw_outs) if raw_outs.isdigit() else None
        if entered_outs is None:
            outs_errors = "abs err: -- · % err: --"
        else:
            absolute = abs(entered_outs - self.expected_outs)
            percentage = absolute / self.expected_outs * 100
            outs_errors = f"abs err: {absolute} · % err: {percentage:.1f}%"
        self.query_one("#outs-result", Static).update(
            f"{self.expected_outs} · {outs_errors}"
        )

        raw_odds = self.query_one("#odds-against", Input).value.strip()
        entered_odds = parse_ratio(raw_odds)
        if entered_odds is None:
            odds_errors = "abs err: -- · % err: --"
        else:
            absolute = abs(entered_odds - self.expected_odds)
            percentage = absolute / self.expected_odds * 100
            odds_errors = f"abs err: {absolute:.2f} · % err: {percentage:.1f}%"
        self.query_one("#odds-result", Static).update(
            f"{self.expected_odds:.1f}:1 · {odds_errors}"
        )
