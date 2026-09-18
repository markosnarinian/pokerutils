import random
import unittest
from unittest.mock import patch

from pokerkit import Automation, Card, NoLimitTexasHoldem
from textual.widgets import Button, Input, Static

from pokertools.app import PokertoolsApp
from pokertools.utils.simulation import Simulation
from pokertools.widgets.playing_card import PlayingCard, Rank, Suit


class SimulationTests(unittest.TestCase):
    def test_blinds_rotation_and_betting_order(self):
        g = Simulation()
        for button in range(6):
            self.assertEqual(g.button, button)
            self.assertEqual(g.seats[5], button)
            self.assertEqual(g.seats[:2], [(button + 1) % 6, (button + 2) % 6])
            self.assertEqual(g.state.bets, [1, 2, 0, 0, 0, 0])
            self.assertEqual(g.state.total_pot_amount, 3)
            for actor in (2, 3, 4, 5, 0, 1):
                self.assertEqual(g.state.actor_index, actor)
                g.act("call")
            self.assertEqual(g.street, "Flop")
            self.assertEqual(g.state.actor_index, 0)
            self.assertEqual(g.state.total_pot_amount, 12)
            self.assertEqual(g.state.bets, [0] * 6)
            g.new_hand()

    def test_pot_odds_include_bets_but_not_future_call(self):
        g = Simulation()
        g.act("raise", 7)
        g.act("fold")
        g.act("call")
        self.assertEqual(g.state.actor_index, g.hero)
        self.assertEqual(g.state.total_pot_amount, 17)
        self.assertAlmostEqual(g.call_odds(), 17 / 7)
        with self.assertRaises(ValueError):
            g.act("raise", 8)
        self.assertEqual(g.state.total_pot_amount, 17)
        g.act("raise", 200)
        self.assertIsNone(g.call_odds())

    def test_draw_odds_only_use_visible_cards(self):
        g = Simulation()
        automations = tuple(
            a
            for a in Automation
            if a not in (Automation.HOLE_DEALING, Automation.BOARD_DEALING)
        )
        g.state = NoLimitTexasHoldem.create_state(
            automations, True, 0, (1, 2), 2, 200, 6
        )
        for cards in ("2c3c", "4c5c", "6c7c", "8c9c", "TcJc", "AhKh"):
            g.state.deal_hole(cards)
        for _ in range(6):
            g.state.check_or_call()
        g.state.deal_board("2h7hQs")
        name, outs, odds = g.draw_question()
        self.assertIn("Flush", name)
        self.assertEqual(outs, 9)
        self.assertAlmostEqual(odds, 38 / 9)
        for _ in range(6):
            g.state.check_or_call()
        g.state.deal_board("3d")
        self.assertAlmostEqual(g.draw_question()[2], 37 / 9)

    def test_side_pots_and_settlement(self):
        g = Simulation()
        g.state = NoLimitTexasHoldem.create_state(
            tuple(Automation), True, 0, (1, 2), 2, (30, 80, 200, 200, 200, 200), 6
        )
        g.act("raise", 200)
        for _ in range(3):
            g.act("fold")
        g.act("call")
        g.act("call")
        self.assertFalse(g.state.status)
        self.assertEqual(sum(g.state.stacks), 910)
        self.assertEqual(sum(g.state.payoffs), 0)
        self.assertEqual(g.state.total_pot_amount, 0)
        # The deep player cannot lose more than the second-deepest caller's 80.
        self.assertGreaterEqual(g.state.stacks[2], 120)

    def test_bot_hands_complete_and_conserve_chips(self):
        random.seed(401)
        g = Simulation()
        for hand in range(60):
            for _ in range(150):
                s = g.state
                if not s.status:
                    break
                if s.actor_index == g.hero:
                    if hand % 3 == 0 and s.can_fold():
                        g.act("fold")
                    elif hand % 3 == 1 and s.can_complete_bet_or_raise_to():
                        g.act("raise", s.max_completion_betting_or_raising_to_amount)
                    else:
                        g.act("call")
                else:
                    g.step()
                self.assertEqual(sum(s.stacks) + s.total_pot_amount, 1200)
                self.assertTrue(all(stack >= 0 for stack in s.stacks))
            self.assertFalse(g.state.status)
            self.assertEqual(sum(g.state.payoffs), 0)
            g.new_hand()


class TrainerTests(unittest.IsolatedAsyncioTestCase):
    async def test_card_widgets_reveal_and_reset(self):
        with (
            patch("pokertools.app.save_theme"),
            patch("pokertools.app.load_theme", return_value=None),
        ):
            app = PokertoolsApp()
            async with app.run_test(size=(120, 48)) as pilot:
                await pilot.press("t")
                await pilot.pause()
                screen = app.screen
                g = screen.game
                g.hero_cards = tuple(Card.parse("ThAc"))
                screen.render_game()
                hero = list(screen.query_one("#seat-0").query(PlayingCard))
                self.assertEqual(
                    [(c.rank, c.suit, c.face_up) for c in hero],
                    [(Rank.TEN, Suit.HEARTS, True), (Rank.ACE, Suit.CLUBS, True)],
                )
                board = list(screen.query_one("#board-cards").query(PlayingCard))
                self.assertEqual(len(board), 5)
                for visible in (0, 3, 4, 5):
                    while len(g.board) < visible:
                        g.act("call")
                    screen.render_game()
                    self.assertEqual(
                        [c.face_up for c in board],
                        [True] * visible + [False] * (5 - visible),
                    )
                    for seat in range(1, 6):
                        self.assertTrue(
                            all(
                                not c.face_up
                                for c in screen.query_one(f"#seat-{seat}").query(
                                    PlayingCard
                                )
                            )
                        )
                g.new_hand()
                screen.render_game()
                self.assertTrue(all(not c.face_up for c in board))
                self.assertTrue(all(c.face_up for c in hero))

    async def test_navigation_answers_invalid_raise_and_completion(self):
        with (
            patch("pokertools.app.save_theme"),
            patch("pokertools.app.load_theme", return_value=None),
        ):
            app = PokertoolsApp()
            async with app.run_test(size=(120, 48)) as pilot:
                await pilot.press("t")
                await pilot.pause()
                screen = app.screen
                self.assertTrue(screen.query_one("#call", Button).disabled)
                screen.query_one("#pot", Input).value = "3"
                screen.query_one("#reveal").scroll_visible(animate=False)
                await pilot.pause()
                await pilot.click("#reveal")
                self.assertIn(
                    "Correct", str(screen.query_one("#feedback", Static).content)
                )
                g = screen.game
                g.act("raise", 7)
                g.act("fold")
                g.act("call")
                screen.render_game()
                await pilot.pause()
                self.assertFalse(screen.query_one("#call", Button).disabled)
                screen.query_one("#pot-odds", Input).value = "2.43:1"
                screen.reveal()
                self.assertIn(
                    "29.2%", str(screen.query_one("#feedback", Static).content)
                )
                self.assertIn(
                    "Correct", str(screen.query_one("#feedback", Static).content)
                )
                screen.query_one("#raise-to", Input).value = "8"
                await pilot.click("#raise")
                self.assertIn(
                    "Invalid action", str(screen.query_one("#feedback", Static).content)
                )
                self.assertEqual(g.state.actor_index, g.hero)
                await pilot.click("#call")
                self.assertNotEqual(g.state.actor_index, g.hero)
                while g.state.status:
                    g.act("call")
                screen.render_game()
                await pilot.pause()
                self.assertFalse(screen.query_one("#new", Button).disabled)
                await pilot.click("#new")
                self.assertEqual(g.hand, 2)
                await pilot.press("escape", "r")
                self.assertIsNot(app.screen, screen)


if __name__ == "__main__":
    unittest.main()
