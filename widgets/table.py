"""A widget that displays the poker table."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical

from widgets.community_cards import CommunityCards
from widgets.player_hand import PlayerHand


class Table(Vertical):
    """The poker table, showing the community cards and the player's hand."""

    def compose(self) -> ComposeResult:
        yield CommunityCards()
        yield PlayerHand()
