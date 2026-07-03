"""Hand evaluation, draw detection, and odds calculations."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from widgets.playing_card import PlayingCard, Rank, Suit

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


def _straight_windows(values: set[int]) -> list[tuple[int, set[int]]]:
    """Return (window_low, missing_ranks) for every 5-wide run missing 1 or 2 ranks."""
    ranks = set(values)
    if 14 in ranks:
        ranks.add(1)  # ace also plays low, for the wheel (A-2-3-4-5)
    windows = []
    for low in range(1, 11):
        window = set(range(low, low + 5))
        missing = window - ranks
        if 1 <= len(missing) <= 2:
            windows.append((low, missing))
    return windows


def _straight_name(high: int) -> str:
    if high == 14:
        return "Broadway Straight"
    if high == 5:
        return "The Wheel"
    return f"{_name(high)}-High Straight"


@dataclass
class HandResult:
    category: int
    tiebreak: tuple
    description: str


def evaluate_five(cards: list[Card], hole_cards: set[Card] | None = None) -> HandResult:
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
        if straight_high == 14:
            description = "Royal Flush"
        elif straight_high == 5:
            description = "Steel Wheel"
        else:
            description = f"{_name(straight_high)}-High Straight Flush"
        return HandResult(8, (straight_high,), description)
    if count_sizes[0] == 4:
        return HandResult(
            7, (count_values[0], count_values[1]), f"Quad {_plural(count_values[0])}"
        )
    if count_sizes[0] == 3 and count_sizes[1] == 2:
        return HandResult(
            6,
            (count_values[0], count_values[1]),
            f"Full House, {_plural(count_values[0])} full of {_plural(count_values[1])}",
        )
    if flush:
        return HandResult(
            5, tuple(sorted(values, reverse=True)), f"{_name(max(values))}-High Flush"
        )
    if straight_high:
        return HandResult(4, (straight_high,), _straight_name(straight_high))
    if count_sizes[0] == 3:
        trip_rank = count_values[0]
        is_set = (
            hole_cards is not None
            and sum(1 for card in cards if card[0] == trip_rank and card in hole_cards) >= 2
        )
        label = f"Set of {_plural(trip_rank)}" if is_set else f"Trip {_plural(trip_rank)}"
        return HandResult(3, tuple(count_values), label)
    if count_sizes[0] == 2 and count_sizes[1] == 2:
        hi, lo = sorted(count_values[:2], reverse=True)
        return HandResult(2, (hi, lo, count_values[2]), f"Two Pair, {_plural(hi)} and {_plural(lo)}")
    if count_sizes[0] == 2:
        return HandResult(1, tuple(count_values), f"Pair of {_plural(count_values[0])}")
    top5 = sorted(values, reverse=True)
    return HandResult(0, tuple(top5), f"{_name(top5[0])} High")


def evaluate_best(cards: list[Card], hole_cards: set[Card] | None = None) -> HandResult:
    """Evaluate the best 5-card hand out of 5, 6, or 7 known cards."""
    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate a hand")
    return max(
        (evaluate_five(list(combo), hole_cards) for combo in combinations(cards, 5)),
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
    chance: float | None = None
    odds_against: float | None = None


def detect_draws(cards: list[Card], unseen: int, cards_to_come: int) -> list[Draw]:
    """Detect flush, straight, gutshot, and backdoor draws among 5, 6, or 7 known cards."""
    if len(cards) < 5:
        return []

    made = evaluate_best(cards)
    draws: list[Draw] = []
    values = {value for value, _ in cards}

    suit_counts = Counter(suit for _, suit in cards)
    for suit, count in suit_counts.items():
        if count == 4:
            draws.append(Draw(f"Flush Draw ({suit.value})", 13 - count))
        elif count == 3 and cards_to_come == 2 and unseen >= 2:
            backdoor_outs = 13 - count
            chance = math.comb(backdoor_outs, 2) / math.comb(unseen, 2) * 100
            odds = (100 - chance) / chance if chance > 0 else math.inf
            draws.append(Draw(f"Backdoor Flush Draw ({suit.value})", backdoor_outs, chance, odds))

    if made.category < 4:
        windows = _straight_windows(values)

        real_missing: dict[int, bool] = {}
        for low, missing in windows:
            if len(missing) != 1:
                continue
            missing_val = next(iter(missing))
            real_val = 14 if missing_val == 1 else missing_val
            is_edge = missing_val in (low, low + 4)
            real_missing[real_val] = real_missing.get(real_val, False) or is_edge

        if len(real_missing) == 1:
            draws.append(Draw("Gutshot Straight Draw", 4))
        elif len(real_missing) == 2:
            if all(real_missing.values()):
                draws.append(Draw("Open-Ended Straight Draw", 8))
            else:
                draws.append(Draw("Double Gutshot Straight Draw", 8))
        elif len(real_missing) > 2:
            draws.append(Draw("Straight Draw", 4 * len(real_missing)))

        if cards_to_come == 2 and unseen >= 2:
            backdoor_pairs: set[frozenset[int]] = set()
            for low, missing in windows:
                if len(missing) != 2:
                    continue
                backdoor_pairs.add(frozenset(14 if v == 1 else v for v in missing))

            for pair in backdoor_pairs:
                if pair & real_missing.keys():
                    continue  # already a direct out on one of these ranks
                hi, lo = sorted(pair, reverse=True)
                chance = 4 * 4 / math.comb(unseen, 2) * 100
                odds = (100 - chance) / chance if chance > 0 else math.inf
                draws.append(
                    Draw(f"Backdoor Straight Draw ({_name(hi)}-{_name(lo)})", 8, chance, odds)
                )

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


@dataclass
class Summary:
    hole_text: str
    hand_desc: str
    draws_text: str
    unseen: int


def summarize(hole: list[PlayingCard], board: list[PlayingCard]) -> Summary:
    """Summarize hand strength, draws, and unseen cards for display."""
    hole_cards = to_cards((card.rank, card.suit) for card in hole)
    revealed = [card for card in board if card.face_up]
    board_cards = to_cards((card.rank, card.suit) for card in revealed)
    known = hole_cards + board_cards

    if len(known) >= 5:
        hand_desc = evaluate_best(known, set(hole_cards)).description
    else:
        hand_desc = describe_hole_cards(hole_cards) if hole_cards else "--"

    hole_text = " ".join(f"{card.rank.value}{card.suit.value}" for card in hole)

    unseen = DECK_SIZE - len(known)
    cards_to_come = {3: 2, 4: 1}.get(len(revealed), 0)

    if cards_to_come and known:
        draws = detect_draws(known, unseen, cards_to_come)
        if draws:
            lines = []
            for draw in draws:
                if draw.chance is None:
                    chance, odds = draw_odds(draw.outs, unseen, cards_to_come)
                else:
                    chance, odds = draw.chance, draw.odds_against
                lines.append(f"- **{draw.name}**")
                lines.append(f"    - {draw.outs} outs")
                lines.append(f"    - {chance:.1f}% chance")
                if odds != math.inf:
                    lines.append(f"    - {odds:.1f} : 1 against")
            draws_text = "\n".join(lines)
        else:
            draws_text = "_None_"
    else:
        draws_text = "_--_"

    return Summary(hole_text=hole_text, hand_desc=hand_desc, draws_text=draws_text, unseen=unseen)
