import unittest

from matchTeams import Team, Player, Double


class TeamTests(unittest.TestCase):
    def test_defaults(self):
        t = Team("Alice")
        self.assertEqual(t.name, "Alice")
        self.assertEqual(t.seedNumber, 0)
        self.assertFalse(t.isSeed)

    def test_seed_inferred_from_seed_number(self):
        self.assertTrue(Team("Bob", seedNumber=3).isSeed)
        self.assertFalse(Team("Carl", seedNumber=0).isSeed)

    def test_explicit_is_seed_overrides_inference(self):
        self.assertTrue(Team("Dan", seedNumber=0, isSeed=True).isSeed)
        self.assertFalse(Team("Eve", seedNumber=5, isSeed=False).isSeed)


class PlayerTests(unittest.TestCase):
    def test_is_present_default(self):
        p = Player("Ana")
        self.assertFalse(p.isPresent)
        self.assertEqual(p.seedNumber, 0)

    def test_inherits_seed_behaviour(self):
        self.assertTrue(Player("Bia", seedNumber=1).isSeed)

    def test_present_flag(self):
        self.assertTrue(Player("Cida", isPresent=True).isPresent)


class DoubleTests(unittest.TestCase):
    def test_name_is_joined(self):
        d = Double(Player("Ana"), Player("Bia"))
        self.assertEqual(d.name, "Ana/Bia")

    def test_keeps_players(self):
        p1, p2 = Player("Ana"), Player("Bia")
        d = Double(p1, p2, seedNumber=2)
        self.assertIs(d.player1, p1)
        self.assertIs(d.player2, p2)
        self.assertTrue(d.isSeed)


if __name__ == "__main__":
    unittest.main()
