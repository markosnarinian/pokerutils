"""Hand evaluation, draw detection, and odds calculations."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from widgets.playing_card import Rank, Suit

RANK_VALUES = {
    Rank.TWO: 2,
    Rank.THREE: 3,
    Rank.FOUR: 4,
    Rank.FIVE: 5,
    Rank.SIX: 6,
    Rank.SEVEN: 7,
    Rank.EIGHT: 8,
    Rank.NINE: 9,
    Rank.TEN: 10,
    Rank.JACK: 11,
    Rank.QUEEN: 12,
    Rank.KING: 13,
    Rank.ACE: 14,
}

RANK_NAMES = {
    2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
    8: "Eight", 9: "Nine", 10: "Ten", 11: "Jack", 12: "Queen", 13: "King", 14: "Ace",
}

Card = tuple[int, Suit]

DECK_SIZE = 52


def _name(value: int) -> str:
    return RANK_NAMES[value]


def _plural(value: int) -> str:
    return f"{_name(value)}s"


def to_cards(pairs: Iterable[tuple[Rank, Suit]]) -> list[Card]:
    """Convert (Rank, Suit) pairs into (rank value, Suit) cards."""
    return [(RANK_VALUES[rank], suit) for rank, suit in pairs]


def _is_straight(values: set[int]) -> int | None:
    """Return the high card of a straight within `values`, if any."""
    ranks = set(values)
    if 14 in ranks:
        ranks.add(1)  # ace also plays low, for the wheel (A-2-3-4-5)
    for low in range(10, 0, -1):
        if all(rank in ranks for rank in range(low, low + 5)):
            return low + 4 if low > 1 else 5
    return None


@dataclass
class HandResult:
    category: int
    tiebreak: tuple
    description: str


def evaluate_five(cards: list[Card]) -> HandResult:
    """Rank a single 5-card hand."""
    values = [value for value, _ in cards]
    suits = [suit for _, suit in cards]
    counts = Counter(values)
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], -kv[0]))
    count_sizes = [count for _, count in ordered]
    count_values = [value for value, _ in ordered]
    flush = len(set(suits)) == 1
    straight_high = _is_straight(set(values))

    if straight_high and flush:
        return HandResult(8, (straight_high,), f"Straight Flush, {_name(straight_high)} High")
    if count_sizes[0] == 4:
        return HandResult(
            7, (count_values[0], count_values[1]), f"Four of a Kind, {_plural(count_values[0])}"
        )
    if count_sizes[0] == 3 and count_sizes[1] == 2:
        return HandResult(
            6,
            (count_values[0], count_values[1]),
            f"Full House, {_plural(count_values[0])} full of {_plural(count_values[1])}",
        )
    if flush:
        return HandResult(
            5, tuple(sorted(values, reverse=True)), f"Flush, {_name(max(values))} High"
        )
    if straight_high:
        return HandResult(4, (straight_high,), f"Straight, {_name(straight_high)} High")
    if count_sizes[0] == 3:
        return HandResult(3, tuple(count_values), f"Three of a Kind, {_plural(count_values[0])}")
    if count_sizes[0] == 2 and count_sizes[1] == 2:
        hi, lo = sorted(count_values[:2], reverse=True)
        return HandResult(2, (hi, lo, count_values[2]), f"Two Pair, {_plural(hi)} and {_plural(lo)}")
    if count_sizes[0] == 2:
        return HandResult(1, tuple(count_values), f"Pair of {_plural(count_values[0])}")
    top5 = sorted(values, reverse=True)
    return HandResult(0, tuple(top5), f"High Card, {_name(top5[0])}")


def evaluate_best(cards: list[Card]) -> HandResult:
    """Evaluate the best 5-card hand out of 5, 6, or 7 known cards."""
    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate a hand")
    return max(
        (evaluate_five(list(combo)) for combo in combinations(cards, 5)),
        key=lambda result: (result.category, result.tiebreak),
    )


def describe_hole_cards(cards: list[Card]) -> str:
    """Describe two hole cards before any community cards are known."""
    (v1, s1), (v2, s2) = cards
    if v1 == v2:
        return f"Pocket {_plural(v1)}"
    hi, lo = sorted((v1, v2), reverse=True)
    suited = " suited" if s1 == s2 else ""
    return f"{_name(hi)}-{_name(lo)}{suited}"


@dataclass
class Draw:
    name: str
    outs: int


def _straight_completing_values(values: set[int]) -> set[int]:
    """Which single rank values, if drawn, would complete a straight."""
    ranks = set(values)
    if 14 in ranks:
        ranks.add(1)
    completing = set()
    for candidate in range(2, 15):
        if candidate in ranks:
            continue
        trial = ranks | {candidate}
        if candidate == 14:
            trial.add(1)
        if _is_straight(trial) is not None:
            completing.add(candidate)
    return completing


def detect_draws(cards: list[Card]) -> list[Draw]:
    """Detect flush and straight draws among 5, 6, or 7 known cards."""
    if len(cards) < 5:
        return []

    made = evaluate_best(cards)
    draws: list[Draw] = []

    suit_counts = Counter(suit for _, suit in cards)
    for suit, count in suit_counts.items():
        if count == 4:
            draws.append(Draw(f"Flush Draw ({suit.value})", 13 - count))

    if made.category < 4:
        completing = _straight_completing_values({value for value, _ in cards})
        if completing:
            outs = 4 * len(completing)
            if outs == 8:
                name = "Open-Ended Straight Draw"
            elif outs == 4:
                name = "Gutshot Straight Draw"
            else:
                name = "Straight Draw"
            draws.append(Draw(name, outs))

    return draws


def draw_odds(outs: int, unseen: int, cards_to_come: int) -> tuple[float, float]:
    """Return (chance percent, odds against) of hitting an out."""
    if cards_to_come <= 0 or unseen <= 0 or outs <= 0:
        return 0.0, math.inf

    miss = math.comb(unseen - outs, cards_to_come) if unseen - outs >= cards_to_come else 0
    total = math.comb(unseen, cards_to_come)
    chance = 1 - (miss / total)
    odds_against = (1 - chance) / chance if chance > 0 else math.inf
    return chance * 100, odds_against
