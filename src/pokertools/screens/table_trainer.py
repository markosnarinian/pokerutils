"""An action-by-action table and hidden-answer arithmetic practice."""

import math
import random
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from ..utils.simulation import Simulation
from ..widgets.playing_card import PlayingCard, Rank, Suit


class TableTrainer(Screen):
    BINDINGS: ClassVar = [
        ("r", "app.pop_screen", "Return"),
        ("escape", "blur", "Remove focus"),
        ("n", "step", "Next action"),
        ("f", "press('fold')", "Fold"),
        ("c", "press('call')", "Check/Call"),
        ("b", "focus_field('raise-to')", "Bet/Raise"),
        ("h", "press('new')", "New hand"),
        ("p", "focus_field('pot')", "Pot"),
        ("e", "focus_field('pot-odds')", "Pot odds"),
        ("d", "focus_field('against')", "Draw odds"),
        ("v", "press('reveal')", "Reveal"),
        ("a", "toggle_auto", "Auto-continue"),
        ("i", "focus_field('average-delay')", "Avg delay"),
        ("j", "focus_field('delay-jitter')", "Jitter"),
        ("u", "press('apply-timing')", "Apply timing"),
    ]
    ANSWER_FIELDS: ClassVar = ("pot", "pot-odds", "against")
    DEFAULT_CSS = """
    TableTrainer #trainer { height: 1fr; padding: 1 2; overflow-x: auto; }
    TableTrainer #pacing { height: auto; overflow-x: auto; }
    TableTrainer #pacing Label { padding: 1 1 0 0; }
    TableTrainer #pacing Input { width: 12; }
    TableTrainer #auto-status { height: auto; margin-bottom: 1; }
    TableTrainer #felt { border: round $success; padding: 1 2; height: auto; min-width: 87; }
    TableTrainer .seat-row { height: auto; }
    TableTrainer .seat { width: 1fr; height: auto; border: round $surface-lighten-2; padding: 0 1; }
    TableTrainer .cards { height: 7; align-horizontal: center; }
    TableTrainer .seat-info { height: auto; text-align: center; }
    TableTrainer .acting { border: round $warning; }
    TableTrainer .folded { border: dashed $surface-lighten-1; }
    TableTrainer .folded .seat-info { color: $text-disabled; }
    TableTrainer .folded PlayingCard { opacity: 25%; }
    TableTrainer #board { height: auto; text-align: center; padding: 1 0; }
    TableTrainer #actions { height: auto; margin: 1 0; layout: horizontal; overflow-x: auto; }
    TableTrainer Button { min-width: 12; margin-right: 1; }
    TableTrainer Input { width: 22; margin-right: 1; }
    TableTrainer #questions { height: auto; margin: 1 0; overflow-x: auto; }
    TableTrainer #feedback { height: auto; color: $accent; }
    TableTrainer #history { height: auto; border-top: solid $primary; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="trainer"):
            with Horizontal(id="pacing"):
                yield Button("Auto: Off (A)", id="auto")
                yield Label("Average s (I)")
                yield Input("3", id="average-delay", type="number")
                yield Label("Jitter ± s (J)")
                yield Input("1", id="delay-jitter", type="number")
                yield Button("Apply timing (U)", id="apply-timing")
            yield Static("Auto-continue off", id="auto-status", markup=False)
            with Vertical(id="felt"):
                for row in ((2, 3, 4), (1, 0, 5)):
                    if row == (1, 0, 5):
                        yield Static(id="board", markup=False)
                        with Horizontal(id="board-cards", classes="cards"):
                            for _ in range(5):
                                yield PlayingCard(Rank.ACE, Suit.SPADES, face_up=False)
                    with Horizontal(classes="seat-row"):
                        for seat in row:
                            with Vertical(id=f"seat-{seat}", classes="seat"):
                                yield Static(classes="seat-info", markup=False)
                                with Horizontal(classes="cards"):
                                    for _ in range(2):
                                        yield PlayingCard(
                                            Rank.ACE, Suit.SPADES, face_up=False
                                        )
            with Horizontal(id="actions"):
                yield Button("Next action (N)", id="step")
                yield Button("Fold (F)", id="fold")
                yield Button("Check / Call (C)", id="call")
                yield Input(placeholder="Raise TO total (B)", id="raise-to", type="integer")
                yield Button("Bet / Raise (B)", id="raise")
                yield Button("New hand (H)", id="new")
            yield Static(id="prompt", markup=False)
            with Horizontal(id="questions"):
                yield Input(placeholder="Pot (chips) (P)", id="pot", type="number")
                yield Input(placeholder="Pot odds X:1 (E)", id="pot-odds")
                yield Input(placeholder="Draw against X:1 (D)", id="against")
                yield Button("Check / Reveal (V)", id="reveal")
            yield Static(id="feedback", markup=False)
            yield Static(id="history", markup=False)
        yield Footer()

    def on_mount(self):
        self.auto_continue = False
        self.average_delay = 3.0
        self.delay_jitter = 1.0
        self.auto_timer = None
        self.timer_generation = 0
        self.game = Simulation()
        self.render_game()

    def render_game(self):
        g, s = self.game, self.game.state
        lines = [
            f"Hand {g.hand} · {g.street} · Blinds 1/2 · Pot: {'?' if s.status else 'awarded'}"
        ]
        for i in range(6):
            position = "SB" if i == 0 else "BB" if i == 1 else "BTN" if i == 5 else ""
            folded = i in g.folded
            status = (
                "folded"
                if folded
                else "done"
                if not s.status
                else "ALL-IN"
                if not s.stacks[i]
                else "in"
            )
            seat = self.query_one(f"#seat-{g.seats[i]}", Vertical)
            seat.query_one(Static).update(
                f"{'▶ ' if s.actor_index == i else ''}{g.name(i)} · {position} · {status}\nStack {s.stacks[i]} · Bet {s.bets[i]}"
            )
            for index, card in enumerate(seat.query(PlayingCard)):
                self.update_card(card, g.hero_cards[index] if i == g.hero else None)
            seat.set_class(s.actor_index == i, "acting")
            seat.set_class(folded, "folded")
        for index, card in enumerate(self.query_one("#board-cards").query(PlayingCard)):
            self.update_card(card, g.board[index] if index < len(g.board) else None)
        if s.status:
            lines.append(
                f"To act: {g.name(s.actor_index)}"
                + (
                    f" · Call {s.checking_or_calling_amount}"
                    if s.actor_index == g.hero
                    else " · Next action or auto-continue"
                )
            )
        else:
            lines.append(
                "Hand complete. Results below; New hand resets stacks and rotates the button."
            )
        self.query_one("#board", Static).update("\n".join(lines))
        hero_turn = s.actor_index == g.hero
        for action, legal in (
            ("fold", s.can_fold()),
            ("call", s.can_check_or_call()),
            ("raise", s.can_complete_bet_or_raise_to()),
        ):
            self.query_one(f"#{action}", Button).disabled = not (hero_turn and legal)
        self.query_one("#step", Button).disabled = not s.status or hero_turn
        self.query_one("#new", Button).disabled = s.status
        self.query_one("#raise-to", Input).disabled = not (
            hero_turn and s.can_complete_bet_or_raise_to()
        )
        self.query_one("#raise-to", Input).placeholder = (
            f"To: {s.min_completion_betting_or_raising_to_amount}–{s.max_completion_betting_or_raising_to_amount} (B)"
            if hero_turn and s.can_complete_bet_or_raise_to()
            else "Raise TO total (B)"
        )
        draw = g.draw_question()
        prompt = "Track the pot, including all current bets. Ratios accept X or X:1.\n"
        prompt += (
            "Pot odds: pot BEFORE your call ÷ call. "
            if g.call_odds() is not None
            else "Pot odds: N/A (no priced hero decision, or all-in/side-pot situation). "
        )
        prompt += (
            f"\n{draw[0]}: {draw[1]} outs. What are the odds AGAINST hitting on the NEXT card?"
            if draw
            else "\nDraw odds: N/A (no direct draw on flop/turn)."
        )
        self.query_one("#prompt", Static).update(prompt)
        self.query_one("#pot", Input).disabled = not s.status
        self.query_one("#reveal", Button).disabled = not s.status
        self.query_one("#pot-odds", Input).disabled = g.call_odds() is None
        self.query_one("#against", Input).disabled = draw is None
        self.query_one("#feedback", Static).update("" if s.status else g.history[-1])
        for field in ("pot", "pot-odds", "against", "raise-to"):
            self.query_one(f"#{field}", Input).value = ""
        self.query_one("#history", Static).update(
            "ACTION HISTORY\n" + "\n".join(g.history)
        )
        self.schedule_auto()
        self.refresh_bindings()

    def cancel_auto(self):
        self.timer_generation += 1
        if self.auto_timer is not None:
            self.auto_timer.stop()
            self.auto_timer = None

    def schedule_auto(self):
        self.cancel_auto()
        status = self.query_one("#auto-status", Static)
        if not self.auto_continue:
            status.update("Auto-continue off · Press A to enable")
            return
        if self.app.screen is not self:
            return
        if not self.game.state.status:
            status.update("Auto-continue paused · Hand complete")
            return
        if self.game.state.actor_index == self.game.hero:
            status.update("Auto-continue paused · Your turn")
            return
        delay = random.uniform(
            self.average_delay - self.delay_jitter,
            self.average_delay + self.delay_jitter,
        )
        generation = self.timer_generation

        def advance():
            if (
                generation == self.timer_generation
                and self.app.screen is self
                and self.auto_continue
            ):
                self.action_step()

        self.auto_timer = self.set_timer(delay, advance)
        status.update(f"Auto-continue on · Next action in {delay:.1f}s · A to pause")

    def action_toggle_auto(self):
        self.auto_continue = not self.auto_continue
        self.query_one("#auto", Button).label = (
            "Auto: On (A)" if self.auto_continue else "Auto: Off (A)"
        )
        self.schedule_auto()

    def apply_timing(self):
        try:
            average = float(self.query_one("#average-delay", Input).value)
            jitter = float(self.query_one("#delay-jitter", Input).value)
            if not (
                math.isfinite(average)
                and math.isfinite(jitter)
                and math.isfinite(average + jitter)
                and jitter >= 0
                and average - jitter >= 0.1
            ):
                raise ValueError
        except ValueError:
            self.query_one("#auto-status", Static).update(
                "Invalid timing: use finite seconds, jitter ≥ 0 and average − jitter ≥ 0.1. Previous timing retained."
            )
            return
        self.average_delay, self.delay_jitter = average, jitter
        self.schedule_auto()

    def on_screen_suspend(self):
        if hasattr(self, "game"):
            self.cancel_auto()

    def on_screen_resume(self):
        if hasattr(self, "game"):
            self.schedule_auto()

    def on_unmount(self):
        self.cancel_auto()

    @staticmethod
    def update_card(widget: PlayingCard, card):
        """Only pass visible cards into the UI; unknown cards remain face-down."""
        widget.face_up = card is not None
        if card is not None:
            widget.rank = Rank("10" if card.rank.value == "T" else card.rank.value)
            widget.suit = {
                "c": Suit.CLUBS,
                "d": Suit.DIAMONDS,
                "h": Suit.HEARTS,
                "s": Suit.SPADES,
            }[card.suit.value]

    def action_blur(self):
        self.set_focus(None)

    def action_step(self):
        if self.game.state.actor_index in (None, self.game.hero):
            return
        self.game.step()
        self.render_game()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Grey out shortcuts whose button or field is currently disabled."""
        if action == "step":
            target = "step"
        elif action in ("press", "focus_field"):
            target = parameters[0]
        else:
            return True
        try:
            return None if self.query_one(f"#{target}").disabled else True
        except NoMatches:
            return True

    def action_press(self, button_id: str):
        self.perform(button_id)

    def action_focus_field(self, field_id: str):
        self.query_one(f"#{field_id}", Input).focus()

    def on_button_pressed(self, event: Button.Pressed):
        self.perform(event.button.id)

    def on_input_submitted(self, event: Input.Submitted):
        field = event.input.id
        if field == "raise-to":
            self.perform("raise")
        elif field in ("average-delay", "delay-jitter"):
            self.perform("apply-timing")
        elif field in self.ANSWER_FIELDS:
            remaining = self.ANSWER_FIELDS[self.ANSWER_FIELDS.index(field) + 1 :]
            for name in remaining:
                if not self.query_one(f"#{name}", Input).disabled:
                    self.query_one(f"#{name}", Input).focus()
                    return
            self.set_focus(None)
            self.perform("reveal")

    def perform(self, action: str):
        try:
            if action == "auto":
                self.action_toggle_auto()
                return
            if action == "apply-timing":
                self.apply_timing()
                return
            if action == "reveal":
                self.reveal()
                return
            if action == "new":
                self.game.new_hand()
            elif action == "step":
                self.game.step()
            elif action in ("fold", "call", "raise"):
                amount = (
                    int(self.query_one("#raise-to", Input).value)
                    if action == "raise"
                    else None
                )
                self.game.act(action, amount)
            self.render_game()
        except ValueError as error:
            self.query_one("#feedback", Static).update(f"Invalid action: {error}")

    def reveal(self):
        g = self.game
        if not g.state.status:
            self.query_one("#feedback", Static).update(
                "The pot has been awarded. See net results in the action history."
            )
            return
        values = [("pot", "Pot", g.state.total_pot_amount, " chips")]
        odds = g.call_odds()
        if odds is not None:
            values.append(("pot-odds", "Pot odds", odds, ":1"))
        draw = g.draw_question()
        if draw:
            values.append(("against", "Next-card odds against", draw[2], ":1"))
        lines = []
        for field, label, expected, unit in values:
            raw = self.query_one(f"#{field}", Input).value.strip()
            try:
                parts = raw.split(":")
                answer = float(parts[0]) / (float(parts[1]) if len(parts) == 2 else 1)
                correct = (
                    len(parts) <= 2
                    and math.isfinite(answer)
                    and abs(answer - expected) <= (0 if field == "pot" else 0.1)
                )
                verdict = "Correct" if correct else "Try again"
            except (ValueError, ZeroDivisionError):
                verdict = "Answer" if not raw else "Invalid number"
            lines.append(f"{label}: {expected:.2f}{unit} · {verdict}")
        if odds is not None:
            lines.append(
                f"Break-even equity: {100 / (odds + 1):.1f}% = call / (pot + call). Excludes future betting and rake."
            )
        if draw:
            unseen = 52 - 2 - len(g.board)
            lines.append(
                f"({unseen} unseen − {draw[1]} outs) / {draw[1]} outs. Making a draw does not guarantee winning."
            )
        self.query_one("#feedback", Static).update("\n".join(lines))
