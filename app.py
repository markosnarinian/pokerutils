from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from widgets import PlayingCard, Rank, Suit


class PokertoolsApp(App):
    TITLE = "pokertools"

    CSS = """
    #table {
        height: 1fr;
    }

    #community-cards {
        height: 1fr;
        align: center middle;
    }

    #hand {
        height: auto;
        align: center middle;
    }

    PlayingCard {
        margin-left: 1;
    }

    PlayingCard:first-of-type {
        margin-left: 0;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical(id="table"):
            with Horizontal(id="community-cards"):
                for _ in range(5):
                    yield PlayingCard(Rank.ACE, Suit.SPADES, face_up=False)
            with Horizontal(id="hand"):
                yield PlayingCard(Rank.ACE, Suit.SPADES)
                yield PlayingCard(Rank.KING, Suit.HEARTS)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
