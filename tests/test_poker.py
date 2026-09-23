import unittest
from types import SimpleNamespace

from pokerutils import widgets
from pokerutils.utils.poker import summarize


def card(
    rank: widgets.Rank, suit: widgets.Suit, *, face_up: bool = True
) -> SimpleNamespace:
    return SimpleNamespace(rank=rank, suit=suit, face_up=face_up)


class OverallOutsTests(unittest.TestCase):
    def test_overlapping_flush_and_straight_outs_are_counted_once(self) -> None:
        hole = [
            card(widgets.Rank.EIGHT, widgets.Suit.HEARTS),
            card(widgets.Rank.NINE, widgets.Suit.HEARTS),
        ]
        board = [
            card(widgets.Rank.SIX, widgets.Suit.HEARTS),
            card(widgets.Rank.SEVEN, widgets.Suit.HEARTS),
            card(widgets.Rank.KING, widgets.Suit.CLUBS),
            card(widgets.Rank.TWO, widgets.Suit.CLUBS, face_up=False),
            card(widgets.Rank.THREE, widgets.Suit.CLUBS, face_up=False),
        ]

        summary = summarize(hole, board)

        self.assertEqual(summary.overall_outs, 15)
        self.assertAlmostEqual(summary.overall_odds_against, 32 / 15)

    def test_other_hand_improvements_are_not_counted_as_flush_outs(self) -> None:
        hole = [
            card(widgets.Rank.SEVEN, widgets.Suit.HEARTS),
            card(widgets.Rank.SEVEN, widgets.Suit.DIAMONDS),
        ]
        board = [
            card(widgets.Rank.SEVEN, widgets.Suit.CLUBS),
            card(widgets.Rank.TWO, widgets.Suit.HEARTS),
            card(widgets.Rank.FOUR, widgets.Suit.HEARTS),
            card(widgets.Rank.NINE, widgets.Suit.HEARTS),
            card(widgets.Rank.THREE, widgets.Suit.CLUBS, face_up=False),
        ]

        summary = summarize(hole, board)

        self.assertEqual(summary.overall_outs, 9)
        self.assertAlmostEqual(summary.overall_odds_against, 37 / 9)


if __name__ == "__main__":
    unittest.main()
