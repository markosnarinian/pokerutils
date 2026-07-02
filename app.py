import random

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header

from widgets import CommunityCards, PlayerHand, PlayingCard, Rank, SidePanel, Suit, Table


class PokertoolsApp(App):
    TITLE = "pokertools"

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("d", "deal", "Deal cards"),
        ("n", "next", "Next round"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal(id="main"):
            yield Table()
            yield SidePanel()
        yield Footer()

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
