"""A bordered panel beside the table showing hand strength, draws, and odds."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Markdown

import poker
from widgets.playing_card import PlayingCard


class SidePanel(Vertical):
    """A panel next to the table showing hand strength, draws, and outs."""

    def compose(self) -> ComposeResult:
        yield Markdown()

    def refresh_info(self, hole: list[PlayingCard], board: list[PlayingCard]) -> None:
        """Recompute and display hand strength, draws, and the unseen-card count."""
        hole_cards = poker.to_cards((card.rank, card.suit) for card in hole)
        revealed = [card for card in board if card.face_up]
        board_cards = poker.to_cards((card.rank, card.suit) for card in revealed)
        known = hole_cards + board_cards

        if len(known) >= 5:
            hand_desc = poker.evaluate_best(known).description
        else:
            hand_desc = poker.describe_hole_cards(hole_cards) if hole_cards else "--"

        hole_text = " ".join(f"{card.rank.value}{card.suit.value}" for card in hole)

        unseen = poker.DECK_SIZE - len(known)
        cards_to_come = {3: 2, 4: 1}.get(len(revealed), 0)

        if cards_to_come and known:
            draws = poker.detect_draws(known)
            if draws:
                lines = []
                for draw in draws:
                    chance, odds = poker.draw_odds(draw.outs, unseen, cards_to_come)
                    odds_text = (
                        f", {odds:.1f} : 1 against" if odds != float("inf") else ""
                    )
                    lines.append(
                        f"- **{draw.name}** — {draw.outs} outs, {chance:.1f}%{odds_text}"
                    )
                draws_text = "\n".join(lines)
            else:
                draws_text = "_None_"
        else:
            draws_text = "_--_"

        markdown = "\n\n".join(
            [
                "## Hand",
                f"**{hole_text}**  \n_{hand_desc}_",
                "## Deck",
                f"**{unseen}** unseen cards",
                "## Draws",
                draws_text,
            ]
        )
        self.query_one(Markdown).update(markdown)
