"""Six-seat practice hands. PokerKit owns all betting and settlement rules."""

import random

from pokerkit import Automation, NoLimitTexasHoldem

from ..widgets.playing_card import Suit
from .poker import detect_draws, draw_odds


class Simulation:
    names = (
        "You",
        "Alex · tight",
        "Sam · loose",
        "Jo · aggressive",
        "Lee · passive",
        "Kim · balanced",
    )

    def __init__(self):
        self.hand = 0
        self.new_hand()

    def new_hand(self):
        """Independent 100-BB drills; move the button one physical seat each hand."""
        self.button = self.hand % 6
        self.hand += 1
        self.seats = [(self.button + 1 + i) % 6 for i in range(6)]
        self.hero = self.seats.index(0)
        self.state = NoLimitTexasHoldem.create_state(
            tuple(Automation),
            True,
            0,
            (1, 2),
            2,
            200,
            6,
        )
        self.hero_cards = tuple(self.state.hole_cards[self.hero])
        self.history = [
            f"Hand {self.hand} · fresh stacks 200 · blinds 1/2",
            f"{self.name(0)} posts small blind 1",
            f"{self.name(1)} posts big blind 2",
        ]

    def name(self, index):
        return self.names[self.seats[index]]

    @property
    def board(self):
        return list(self.state.get_board_cards(0))

    @property
    def street(self):
        return {0: "Preflop", 3: "Flop", 4: "Turn", 5: "River"}[len(self.board)]

    def act(self, action, amount=None):
        state = self.state
        actor = state.actor_index
        if actor is None:
            raise ValueError("This hand is complete.")
        street = self.street
        if action == "fold":
            state.fold()
            description = "folds"
        elif action == "call":
            cost = state.checking_or_calling_amount
            state.check_or_call()
            description = f"calls {cost}" if cost else "checks"
        elif action == "raise":
            state.complete_bet_or_raise_to(amount)
            description = f"bets/raises to {amount}"
        else:
            raise ValueError("Unknown action")
        self.history.append(f"{street} · {self.name(actor)} {description}")
        if self.street != street:
            self.history.append(f"{self.street} · {' '.join(map(repr, self.board))}")
        if not state.status:
            self.history.append(
                "Hand complete · net results: "
                + ", ".join(
                    f"{self.name(i)} {payoff:+}"
                    for i, payoff in enumerate(state.payoffs)
                )
            )

    def step(self):
        """Simple stochastic styles, using only the actor's cards and public board."""
        s = self.state
        i = s.actor_index
        if i is None or i == self.hero:
            return
        cards = s.hole_cards[i]
        ranks = ["23456789TJQKA".index(c.rank.value) for c in cards]
        strength = sum(ranks) / 24 + (0.35 if ranks[0] == ranks[1] else 0)
        if self.board:
            strength = s.get_hand(i, 0, 0).entry.index / 7461
        style = self.seats[i]
        aggression = {1: 0.12, 2: 0.22, 3: 0.42, 4: 0.06, 5: 0.22}[style]
        cost = s.checking_or_calling_amount
        tolerance = {1: 0.25, 2: 0.8, 3: 0.55, 4: 0.65, 5: 0.45}[style]
        if (
            cost
            and random.random() > min(0.95, tolerance + strength * 0.4)
            and s.can_fold()
        ):
            self.act("fold")
        elif random.random() < aggression and s.can_complete_bet_or_raise_to():
            minimum = s.min_completion_betting_or_raising_to_amount
            maximum = s.max_completion_betting_or_raising_to_amount
            target = min(
                maximum, max(minimum, max(s.bets) + max(2, s.total_pot_amount // 2))
            )
            self.act("raise", target)
        else:
            self.act("call")

    def draw_question(self):
        """One direct draw, next-card odds, never conditioned on hidden cards."""
        if (
            not self.state.status
            or len(self.board) not in (3, 4)
            or not self.state.statuses[self.hero]
        ):
            return None
        suits = dict(zip("cdhs", (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES)))
        known = [
            ("23456789TJQKA".index(c.rank.value) + 2, suits[c.suit.value])
            for c in [*self.state.hole_cards[self.hero], *self.board]
        ]
        draws = detect_draws(known, 52 - len(known), 1)
        if not draws:
            return None
        draw = draws[0]
        return draw.name, draw.outs, draw_odds(draw.outs, 52 - len(known), 1)[1]

    def call_odds(self):
        """Only quote simple pot odds when no side-pot eligibility is involved."""
        s = self.state
        if s.actor_index != self.hero or not s.checking_or_calling_amount:
            return None
        if any(active and stack == 0 for active, stack in zip(s.statuses, s.stacks)):
            return None
        if s.checking_or_calling_amount == s.stacks[self.hero]:
            return None
        return s.total_pot_amount / s.checking_or_calling_amount
