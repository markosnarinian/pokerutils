"""A widget that displays the player's own hole cards."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal

from widgets.playing_card import PlayingCard, Rank, Suit


class PlayerHand(Horizontal):
    """The player's hole cards, held face-up at the bottom of the table."""

    def compose(self) -> ComposeResult:
        yield PlayingCard(Rank.ACE, Suit.SPADES)
        yield PlayingCard(Rank.KING, Suit.HEARTS)
