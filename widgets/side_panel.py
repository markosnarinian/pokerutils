"""A bordered panel beside the table showing hand and round information."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from widgets.playing_card import PlayingCard

ROUND_NAMES = {0: "Pre-flop", 3: "Flop", 4: "Turn", 5: "River"}


class SidePanel(Vertical):
    """A panel next to the table showing the current round, hand, and board."""

    def compose(self) -> ComposeResult:
        yield Static("Round: Pre-flop", id="round-info")
        yield Static("Hand: --", id="hand-info")
        yield Static("Board: --", id="board-info")

    def refresh_info(
        self, hand: list[PlayingCard], board: list[PlayingCard]
    ) -> None:
        """Update the panel to reflect the current hand and community cards."""
        revealed = sum(card.face_up for card in board)
        round_name = ROUND_NAMES.get(revealed, ROUND_NAMES[5])

        self.query_one("#round-info", Static).update(f"Round: {round_name}")
        self.query_one("#hand-info", Static).update(f"Hand: {_cards_text(hand)}")
        self.query_one("#board-info", Static).update(f"Board: {_cards_text(board)}")


def _cards_text(cards: list[PlayingCard]) -> str:
    return " ".join(
        f"{card.rank.value}{card.suit.value}" if card.face_up else "??"
        for card in cards
    )
