import random
import unittest

from category import Category
from matchTeams import Player, Double
from tennisEnums import CategoryTypes, MatchTypes, SetTypes, ScoreTypes, MatchWinnerTypes
from tennisExceptions import (
    AddingDoubleInSingleCategory,
    DuplicatedTeam,
)


def single(name="C", ctype=CategoryTypes.RoundRobin, n=0, seeds=0):
    cat = Category(name, ctype, MatchTypes.Single)
    for i in range(1, n + 1):
        cat.AddTeam(Player(f"P{i:02d}", seedNumber=(i if i <= seeds else 0)))
    return cat


class AddTeamTests(unittest.TestCase):
    def test_single_goes_to_teams(self):
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Single)
        cat.AddTeam(Player("A"))
        self.assertIn("A", cat.teams)
        self.assertEqual(len(cat.players), 0)

    def test_player_in_double_category_goes_to_players(self):
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Double)
        cat.AddTeam(Player("A"))
        self.assertIn("A", cat.players)
        self.assertEqual(len(cat.teams), 0)

    def test_double_in_single_category_raises(self):
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Single)
        with self.assertRaises(AddingDoubleInSingleCategory):
            cat.AddTeam(Double(Player("A"), Player("B")))

    def test_duplicate_team_raises(self):
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Single)
        cat.AddTeam(Player("A"))
        with self.assertRaises(DuplicatedTeam):
            cat.AddTeam(Player("A"))


class CategoryTypeTests(unittest.TestCase):
    def test_automatic_round_robin(self):
        cat = single(n=5, ctype=CategoryTypes.Automatic)
        cat.UpdateCategoryType()
        self.assertEqual(cat.categoryType, CategoryTypes.RoundRobin)

    def test_automatic_groups(self):
        cat = single(n=6, ctype=CategoryTypes.Automatic)
        cat.UpdateCategoryType()
        self.assertEqual(cat.categoryType, CategoryTypes.Groups)

    def test_automatic_single_elimination(self):
        cat = single(n=10, ctype=CategoryTypes.Automatic)
        cat.UpdateCategoryType()
        self.assertEqual(cat.categoryType, CategoryTypes.SingleElimination)

    def test_groups_downgraded_to_round_robin(self):
        cat = single(n=5, ctype=CategoryTypes.Groups)
        cat.UpdateCategoryType()
        self.assertEqual(cat.categoryType, CategoryTypes.RoundRobin)

    def test_has_eliminatory_stage(self):
        cat = single(ctype=CategoryTypes.RoundRobin)
        self.assertFalse(cat.HasEliminatoryStage())

        cat = single(ctype=CategoryTypes.Groups)
        self.assertTrue(cat.HasEliminatoryStage())

        cat = single(ctype=CategoryTypes.SingleElimination)
        self.assertTrue(cat.HasEliminatoryStage())


class GroupAndByeMathTests(unittest.TestCase):
    def test_get_number_of_groups(self):
        self.assertEqual(single(n=6).GetNumberOfGroups(), (2, 0))
        self.assertEqual(single(n=7).GetNumberOfGroups(), (1, 1))
        self.assertEqual(single(n=8).GetNumberOfGroups(), (0, 2))
        self.assertEqual(single(n=9).GetNumberOfGroups(), (3, 0))
        self.assertEqual(single(n=11).GetNumberOfGroups(), (1, 2))

    def test_get_number_of_byes(self):
        self.assertEqual(single(n=6).GetNumberOfByes(), 2)
        self.assertEqual(single(n=8).GetNumberOfByes(), 0)
        self.assertEqual(single(n=5).GetNumberOfByes(), 3)

    def test_get_byes_distribution(self):
        cat = single(n=6)
        self.assertEqual(cat.GetByes(3), (2, 0))  # 2 byes, todos com cabeças
        self.assertEqual(cat.GetByes(1), (1, 1))  # 1 com cabeça, 1 sem


class SortTests(unittest.TestCase):
    def test_sort_teams_seeds_first_then_name(self):
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Single)
        cat.AddTeam(Player("Zeca"))
        cat.AddTeam(Player("Ana"))
        cat.AddTeam(Player("Bob", seedNumber=2))
        cat.AddTeam(Player("Cid", seedNumber=1))
        cat.SortTeams()
        self.assertEqual(list(cat.teams.keys()), ["Cid", "Bob", "Ana", "Zeca"])


class FirstRoundTests(unittest.TestCase):
    def test_round_robin_all_pairs(self):
        cat = single(n=4, ctype=CategoryTypes.RoundRobin)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        self.assertEqual(len(cat.matches), 6)  # C(4,2)
        self.assertTrue(all(k[3:5] == "RR" for k in cat.matches))
        self.assertEqual(len(cat.groups), 1)

    def test_groups_creates_group_matches(self):
        random.seed(0)
        cat = single(n=9, ctype=CategoryTypes.Groups, seeds=3)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        self.assertEqual(len(cat.groups), 3)
        gr = [k for k in cat.matches if k[3:5] == "GR"]
        self.assertEqual(len(gr), 9)  # 3 grupos de 3 -> 3 jogos cada

    def test_single_elimination_conserves_all_teams(self):
        random.seed(0)
        cat = single(n=8, ctype=CategoryTypes.SingleElimination, seeds=4)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        appearing = set()
        for m in cat.matches.values():
            for t in (m.team1, m.team2):
                if t is not None:
                    appearing.add(t.name)
        self.assertEqual(appearing, set(cat.teams))


class BracketTests(unittest.TestCase):
    def _elim4(self):
        random.seed(0)
        cat = single(n=4, ctype=CategoryTypes.SingleElimination, seeds=2)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        cat.GetBracket()
        cat.CompleteMatches(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        return cat

    def test_bracket_maps_to_final(self):
        cat = self._elim4()
        self.assertEqual(cat.bracket["002SE001"], "001SE001")
        self.assertEqual(cat.bracket["002SE002"], "001SE001")
        self.assertIsNone(cat.bracket["001SE001"])

    def test_complete_matches_fills_future_rounds(self):
        cat = self._elim4()
        self.assertIn("001SE001", cat.matches)

    def test_update_bracket_promotes_winner(self):
        cat = self._elim4()
        first = cat.matches["002SE001"]
        winner = first.team1
        first.SetScore([(6, 0)], ScoreTypes.Normal)
        self.assertEqual(first.matchWinner, MatchWinnerTypes.Team1)
        cat.UpdateBracket()
        self.assertIs(cat.matches["001SE001"].team1, winner)


class GroupsToEliminationTests(unittest.TestCase):
    def test_full_group_phase_builds_elimination(self):
        random.seed(42)
        cat = single(n=9, ctype=CategoryTypes.Groups, seeds=3)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        cat.GetBracket()
        cat.CompleteMatches(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        for k, m in cat.matches.items():
            if k[3:5] == "GR":
                m.SetScore([(6, 0)], ScoreTypes.Normal)
        cat.UpdateBracket()
        self.assertTrue(cat.isGroupsFinished)
        # 3 grupos -> 6 classificados -> chave de 8 (com byes), todos posicionados
        placed = set()
        for k, m in cat.matches.items():
            if k[3:5] == "SE":
                for t in (m.team1, m.team2):
                    if t is not None:
                        placed.add(t.name)
        self.assertEqual(len(placed), 6)


class GetFirstEliminationStageTests(unittest.TestCase):
    def test_single_elimination(self):
        c = single(ctype=CategoryTypes.SingleElimination, n=5)
        c.GetFirstRound()
        c.GetBracket()
        c.CompleteMatches()
        c.SortMatches()
        c.isInitialized = True
        self.assertEqual(c.GetFirstEliminationStage(), 4)

    def test_round_robin(self):
        c = single(ctype=CategoryTypes.RoundRobin, n=4)
        c.GetFirstRound()
        c.GetBracket()
        c.CompleteMatches()
        c.SortMatches()
        c.isInitialized = True
        self.assertIsNone(c.GetFirstEliminationStage())


class DoublesDrawTests(unittest.TestCase):
    def test_draw_pairs_by_seed_sum(self):
        random.seed(1)
        cat = Category("C", CategoryTypes.RoundRobin, MatchTypes.Double, isRandomDoubles=True)
        for i, seed in enumerate([1, 1, 2, 2]):
            cat.AddTeam(Player(f"J{i}", seedNumber=seed))
        cat.DrawDubles([])
        self.assertEqual(len(cat.teams), 2)
        used = []
        for d in cat.teams.values():
            used += [d.player1.name, d.player2.name]
            seeds = {d.player1.seedNumber, d.player2.seedNumber}
            self.assertEqual(seeds, {1, 2})  # cada dupla = um seed 1 + um seed 2
        self.assertEqual(sorted(used), ["J0", "J1", "J2", "J3"])


class MiscTests(unittest.TestCase):
    def test_get_matches_filter(self):
        cat = single(n=4, ctype=CategoryTypes.RoundRobin)
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        self.assertEqual(cat.GetMatches(), cat.matches)
        self.assertEqual(len(cat.GetMatches("006RR")), 6)
        self.assertEqual(len(cat.GetMatches("ZZZ")), 0)

    def test_teams_summary(self):
        cat = single(n=3, ctype=CategoryTypes.RoundRobin)
        self.assertIn("Quantidade total: 3", cat.GetTeamsSummary())


if __name__ == "__main__":
    unittest.main()
