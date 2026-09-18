"""A panel with a form for entering odds against and outs."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical
from textual.widgets import Button, Input, Label


class AnswerPanel(Vertical):
    """A form, next to the player's hand, for entering odds against and outs."""

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "submit":
            return
        odds_against = self.query_one("#odds-against", Input).value
        outs = self.query_one("#outs", Input).value
        print(f"Odds against: {odds_against}, Outs: {outs}")
