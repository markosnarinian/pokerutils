from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Markdown

from .screens.outs_odds import OutsOdds
from .utils.config import load_theme, save_theme
from .utils.readme import load_readme


class PokertoolsApp(App):
    TITLE = "pokertools"

    CSS_PATH = "app.tcss"

    AUTO_FOCUS = None

    SCREENS = {"outs_odds": OutsOdds}

    BINDINGS = [
        ("o", "push_screen('outs_odds')", "Outs/Odds"),
        Binding("escape", "blur", "Remove focus", show=True),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        saved_theme = load_theme()
        if saved_theme is not None:
            self.theme = saved_theme

    def watch_theme(self, theme: str) -> None:
        save_theme(theme)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Disable navigation to the exercise while it is already open."""
        if action == "push_screen" and parameters == ("outs_odds",):
            return not isinstance(self.screen, OutsOdds)
        return True

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        readme = load_readme()
        yield Header()
        yield Markdown(readme, id="readme")
        yield Footer(show_command_palette=True)
