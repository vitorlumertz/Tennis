import unittest

from tennis_manager.tournament import Tournament
from tennis_manager.category import Category
from tennis_manager.matchTeams import Player
from tennis_manager.tennisEnums import CategoryTypes, MatchTypes
from tennis_manager.tennisExceptions import CategoryNotFound, DuplicatedCategory


def empty_tournament():
    return Tournament("T", sets=1)


class TournamentBasicsTests(unittest.TestCase):
    def test_add_and_get_category(self):
        t = empty_tournament()
        cat = Category("A", CategoryTypes.RoundRobin, MatchTypes.Single)
        t.AddCategory(cat)
        self.assertIs(t.GetCategory("A"), cat)

    def test_duplicate_category_raises(self):
        t = empty_tournament()
        t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
        with self.assertRaises(DuplicatedCategory):
            t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))

    def test_get_missing_category_raises(self):
        with self.assertRaises(CategoryNotFound):
            empty_tournament().GetCategory("nope")

    def test_add_team_delegates_to_category(self):
        t = empty_tournament()
        t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
        t.AddTeam(Player("Ana"), "A")
        self.assertIn("Ana", t.GetCategory("A").teams)

    def test_add_old_double(self):
        t = empty_tournament()
        t.AddOldDouble("Ana", "Bia")
        self.assertEqual(t.oldDoubles, [("Ana", "Bia")])

    def test_repr_contains_name(self):
        self.assertIn("T", repr(empty_tournament()))


class StartCategoryTests(unittest.TestCase):
    def _tournament_with_round_robin(self):
        t = Tournament("T", sets=1)
        cat = Category("A", CategoryTypes.RoundRobin, MatchTypes.Single)
        t.AddCategory(cat)
        for i in range(4):
            t.AddTeam(Player(f"P{i}"), "A")
        return t

    def test_start_category_initializes_and_creates_matches(self):
        t = self._tournament_with_round_robin()
        t.StartCategory("A")
        cat = t.GetCategory("A")
        self.assertTrue(cat.isInitialized)
        self.assertEqual(len(cat.matches), 6)  # C(4,2)

    def test_start_category_idempotent(self):
        t = self._tournament_with_round_robin()
        t.StartCategory("A")
        n = len(t.GetCategory("A").matches)
        t.StartCategory("A")  # já iniciado -> sem efeito
        self.assertEqual(len(t.GetCategory("A").matches), n)

    def test_start_categories_all(self):
        t = self._tournament_with_round_robin()
        t.AddCategory(Category("B", CategoryTypes.RoundRobin, MatchTypes.Single))
        for i in range(3):
            t.AddTeam(Player(f"Q{i}"), "B")
        t.StartCategories()
        self.assertTrue(t.GetCategory("A").isInitialized)
        self.assertTrue(t.GetCategory("B").isInitialized)

    def test_update_brackets_runs(self):
        t = self._tournament_with_round_robin()
        t.StartCategory("A")
        t.UpdateBrackets()  # não deve lançar


if __name__ == "__main__":
    unittest.main()
