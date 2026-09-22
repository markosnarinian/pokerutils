"""A widget that displays the community cards on the table."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal

from .playing_card import PlayingCard, Rank, Suit


class CommunityCards(Horizontal):
    """The row of shared cards dealt face-down in the middle of the table."""

    def compose(self) -> ComposeResult:
        for _ in range(5):
            yield PlayingCard(Rank.ACE, Suit.SPADES, face_up=False)
