from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from widgets import PlayingCard, Rank, Suit


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
            with Vertical(id="table"):
                with Horizontal(id="community-cards"):
                    for _ in range(5):
                        yield PlayingCard(Rank.ACE, Suit.SPADES, face_up=False)
                with Horizontal(id="hand"):
                    yield PlayingCard(Rank.ACE, Suit.SPADES)
                    yield PlayingCard(Rank.KING, Suit.HEARTS)
            yield Vertical(id="side-panel")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
