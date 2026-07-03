import random

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header

from screens import ConfigScreen
from utils.config import load_theme, save_theme
from widgets import (
    AnswerPanel,
    CommunityCards,
    PlayerHand,
    PlayingCard,
    Rank,
    SidePanel,
    Suit,
    Table,
)


class PokertoolsApp(App):
    TITLE = "pokertools"

    CSS_PATH = "app.tcss"

    AUTO_FOCUS = None

    BINDINGS = [
        Binding("d", "deal", "Deal cards"),
        Binding("n", "next", "Next round"),
        Binding("s", "hide_details", "Hide details"),
        Binding("s", "show_details", "Show details"),
        Binding("c", "show_config", "Configuration"),
        Binding("escape", "blur", "Remove focus", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        saved_theme = load_theme()
        if saved_theme is not None:
            self.theme = saved_theme

    def watch_theme(self, theme: str) -> None:
        save_theme(theme)

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

    def action_blur(self) -> None:
        """Remove focus from whichever widget currently has it."""
        self.screen.set_focus(None)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Show only the "hide details" or "show details" binding that currently applies."""
        if action in ("hide_details", "show_details"):
            side_panels = self.query(SidePanel)
            hidden = side_panels.first().hidden if side_panels else False
            return hidden == (action == "show_details")
        return True

    def action_hide_details(self) -> None:
        """Hide the side panel's details behind a shaded pattern."""
        self.query_one(SidePanel).hidden = True
        self.refresh_bindings()

    def action_show_details(self) -> None:
        """Reveal the side panel's details."""
        self.query_one(SidePanel).hidden = False
        self.refresh_bindings()

    def on_answer_panel_submitted(self, message: AnswerPanel.Submitted) -> None:
        self.query_one(SidePanel).show_result(message.odds_against, message.outs)

    def _refresh_side_panel(self) -> None:
        self.query_one(SidePanel).refresh_info(
            list(self.query(PlayerHand).first().query(PlayingCard)),
            list(self.query(CommunityCards).first().query(PlayingCard)),
        )
