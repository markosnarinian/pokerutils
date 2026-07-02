import random

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header

from widgets import (
    CommunityCards,
    PlayerHand,
    PlayingCard,
    Rank,
    SidePanel,
    Suit,
    Table,
)


class PokertoolsApp(App):
    def __init__(self, dev_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.dev_mode = dev_mode

    TITLE = "pokertools"

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("d", "deal", "Deal cards"),
        ("n", "next", "Next round"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal(id="main"):
            yield Table()
            yield SidePanel()
        yield Footer(show_command_palette=True)

    def on_mount(self) -> None:
        self.action_deal()

    def action_deal(self) -> None:
        """Shuffle a fresh deck and deal new hole cards and community cards."""
        deck = [(rank, suit) for suit in Suit for rank in Rank]
        random.shuffle(deck)

        for card in self.query(PlayerHand).first().query(PlayingCard):
            card.rank, card.suit = deck.pop()
            card.face_up = True

        for card in self.query(CommunityCards).first().query(PlayingCard):
            card.rank, card.suit = deck.pop()
            card.face_up = False

        self._refresh_side_panel()

    def action_next(self) -> None:
        """Reveal the flop (3 cards), then the turn, then the river."""
        cards = list(self.query(CommunityCards).first().query(PlayingCard))
        face_down = [card for card in cards if not card.face_up]
        if not face_down:
            return

        reveal_count = 3 if len(face_down) == len(cards) else 1
        for card in face_down[:reveal_count]:
            card.face_up = True

        self._refresh_side_panel()

    def _refresh_side_panel(self) -> None:
        self.query_one(SidePanel).refresh_info(
            list(self.query(PlayerHand).first().query(PlayingCard)),
            list(self.query(CommunityCards).first().query(PlayingCard)),
        )
