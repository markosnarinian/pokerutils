"""A bordered placeholder panel that will hold the recommended play."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class AnswerPanel(Vertical):
    """Placeholder panel, next to the player's hand, for the suggested action."""

    def compose(self) -> ComposeResult:
        yield Static("Answer")
