"""A bordered panel beside the table showing hand strength, draws, and odds."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Markdown

from utils.config import load_odds_error_margin
from utils.poker import AnswerResult, Summary, grade_answer, summarize
from widgets.playing_card import PlayingCard


class SidePanel(Vertical):
    """A panel next to the table showing hand strength, draws, and outs."""

    hidden: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._summary: Summary | None = None

    def compose(self) -> ComposeResult:
        yield Markdown()

    def refresh_info(self, hole: list[PlayingCard], board: list[PlayingCard]) -> None:
        """Recompute and display hand strength, draws, and the unseen-card count."""
        self._summary = summarize(hole, board)
        self._render()

    def show_result(self, odds_against_text: str, outs_text: str) -> None:
        """Grade the player's submitted answers and display the result."""
        if self._summary is None:
            return
        result = grade_answer(
            outs_text, odds_against_text, self._summary, load_odds_error_margin()
        )
        self._render(result)

    def _render(self, result: AnswerResult | None = None) -> None:
        summary = self._summary
        markdown = (
            f"## Hand\n\n**{summary.hole_text}**  \n_{summary.hand_desc}_\n\n"
            f"## Deck\n\n**{summary.unseen}** unseen cards\n\n"
            f"## Draws\n\n{summary.draws_text}"
        )
        if result is not None:
            markdown += (
                "\n\n## Result\n\n"
                f"- Outs: {'Correct' if result.outs_correct else 'Incorrect'}\n"
                f"- Odds against: {'Correct' if result.odds_against_correct else 'Incorrect'}"
            )
        self.query_one(Markdown).update(markdown)
