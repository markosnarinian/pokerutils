from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header

from widgets import SidePanel, Table


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
