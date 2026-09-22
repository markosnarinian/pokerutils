"""A widget that displays a single playing card."""

from __future__ import annotations

from enum import Enum

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static


class Suit(Enum):
    """The suit of a playing card."""

    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"


class Rank(Enum):
    """The rank of a playing card."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


RED_SUITS = {Suit.DIAMONDS, Suit.HEARTS}


class PlayingCard(Static):
    """A single playing card, showing a rank and suit, that can be flipped face-down."""

    DEFAULT_CSS = """
    PlayingCard {
        width: 11;
        height: 7;
    }

    PlayingCard.-face-down {
        background: blue 40%;
        hatch: right white 30%;
    }
    """

    rank: reactive[Rank] = reactive(Rank.ACE)
    suit: reactive[Suit] = reactive(Suit.SPADES)
    face_up: reactive[bool] = reactive(True)

    def __init__(
        self,
        rank: Rank,
        suit: Suit,
        *,
        face_up: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.set_reactive(PlayingCard.rank, rank)
        self.set_reactive(PlayingCard.suit, suit)
        self.set_reactive(PlayingCard.face_up, face_up)
        self.set_class(not face_up, "-face-down")

    def flip(self) -> None:
        """Toggle the card between face-up and face-down."""
        self.face_up = not self.face_up

    def action_flip(self) -> None:
        self.flip()

    def watch_rank(self) -> None:
        self.refresh()

    def watch_suit(self) -> None:
        self.refresh()

    def watch_face_up(self, face_up: bool) -> None:
        self.set_class(not face_up, "-face-down")
        self.refresh()

    def render(self) -> RenderableType:
        if not self.face_up:
            return self._render_back()
        return self._render_face()

    def _render_face(self) -> RenderableType:
        color = "red" if self.suit in RED_SUITS else "black"
        rank = self.rank.value
        suit = self.suit.value

        body = Group(
            Text(f"{rank:<2}{suit}", style=color),
            Text(""),
            Text(suit, style=f"bold {color}", justify="center"),
            Text(""),
            Text(f"{suit}{rank:>2}", style=color, justify="right"),
        )
        return Panel(body, style="on white", border_style=color)

    def _render_back(self) -> RenderableType:
        lines = [
            "  poker",
            "",
            "",
            "",
            "utils",
        ]
        body = Group(*lines)
        return Panel(body, border_style="white")
