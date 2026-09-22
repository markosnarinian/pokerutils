"""A bordered panel beside the table showing hand strength, draws, and odds."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Markdown

from ..utils.poker import Summary, summarize
from .playing_card import PlayingCard


class SidePanel(Vertical):
    """A panel next to the table showing hand strength, draws, and outs."""

    hidden: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        yield Markdown()

    def watch_hidden(self, hidden: bool) -> None:
        """Hide the analysis while preserving the panel's layout."""
        self.set_class(hidden, "-details-hidden")
        for details in self.query(Markdown):
            details.display = not hidden

    def refresh_info(self, hole: list[PlayingCard], board: list[PlayingCard]) -> Summary:
        """Recompute and display hand strength, draws, and the unseen-card count."""
        summary = summarize(hole, board)
        markdown = (
            f"## Hand\n\n**{summary.hole_text}**  \n_{summary.hand_desc}_\n\n"
            f"## Deck\n\n**{summary.unseen}** unseen cards\n\n"
            f"## Draws\n\n{summary.draws_text}"
        )
        self.query_one(Markdown).update(markdown)
        return summary
