import unittest

import tennisHelper as tnh
from match import Match
from matchTeams import Player
from tennisEnums import SetTypes, ScoreTypes, MatchWinnerTypes


class IsValidSetScoreTests(unittest.TestCase):
    def test_equal_is_invalid(self):
        self.assertFalse(tnh.IsValidSetScore((6, 6), SetTypes.NormalSet))

    def test_not_defined_accepts_any_unequal(self):
        self.assertTrue(tnh.IsValidSetScore((3, 1), SetTypes.NotDefined))
        self.assertFalse(tnh.IsValidSetScore((3, 3), SetTypes.NotDefined))

    def test_normal_set(self):
        for score in [(6, 0), (6, 4), (7, 5), (7, 6), (4, 6), (6, 7)]:
            self.assertTrue(tnh.IsValidSetScore(score, SetTypes.NormalSet), score)
        for score in [(6, 5), (8, 6), (5, 3), (6, 6)]:
            self.assertFalse(tnh.IsValidSetScore(score, SetTypes.NormalSet), score)

    def test_short_set(self):
        for score in [(4, 0), (4, 2), (5, 3), (5, 4)]:
            self.assertTrue(tnh.IsValidSetScore(score, SetTypes.ShortSet), score)
        for score in [(4, 3), (6, 4), (3, 1)]:
            self.assertFalse(tnh.IsValidSetScore(score, SetTypes.ShortSet), score)

    def test_long_set(self):
        for score in [(8, 0), (8, 6), (9, 7), (9, 8)]:
            self.assertTrue(tnh.IsValidSetScore(score, SetTypes.LongSet), score)
        for score in [(8, 7), (10, 8)]:
            self.assertFalse(tnh.IsValidSetScore(score, SetTypes.LongSet), score)

    def test_match_tie_break(self):
        for score in [(10, 0), (10, 8), (11, 9), (12, 10)]:
            self.assertTrue(tnh.IsValidSetScore(score, SetTypes.MatchTieBreak), score)
        for score in [(10, 9), (9, 7), (11, 8)]:
            self.assertFalse(tnh.IsValidSetScore(score, SetTypes.MatchTieBreak), score)


class IsValidScoreTests(unittest.TestCase):
    def test_even_sets_invalid(self):
        self.assertEqual(tnh.IsValidScore([(6, 0), (6, 0)], 2), MatchWinnerTypes.NotDefined)

    def test_too_many_sets_invalid(self):
        self.assertEqual(
            tnh.IsValidScore([(6, 0), (6, 0), (6, 0), (6, 0)], 3),
            MatchWinnerTypes.NotDefined,
        )

    def test_none_invalid(self):
        self.assertEqual(tnh.IsValidScore(None, 3), MatchWinnerTypes.NotDefined)

    def test_straight_sets_win(self):
        self.assertEqual(
            tnh.IsValidScore([(6, 4), (6, 3)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
            MatchWinnerTypes.Team1,
        )

    def test_tie_break_decider(self):
        self.assertEqual(
            tnh.IsValidScore([(6, 4), (3, 6), (10, 8)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
            MatchWinnerTypes.Team1,
        )

    def test_team2_wins(self):
        self.assertEqual(
            tnh.IsValidScore([(4, 6), (6, 3), (8, 10)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
            MatchWinnerTypes.Team2,
        )

    def test_single_set_uses_set_type_not_last(self):
        # sets == 1: o único set usa setType (não lastSetType), regressão dos dados de exemplo
        self.assertEqual(
            tnh.IsValidScore([(6, 0)], 1, SetTypes.NormalSet, SetTypes.MatchTieBreak),
            MatchWinnerTypes.Team1,
        )

    def test_short_set_category(self):
        self.assertEqual(
            tnh.IsValidScore([(4, 1), (4, 2)], 3, SetTypes.ShortSet, SetTypes.ShortSet),
            MatchWinnerTypes.Team1,
        )

    def test_invalid_set_inside_score(self):
        self.assertEqual(
            tnh.IsValidScore([(6, 4), (6, 5)], 3, SetTypes.NormalSet, SetTypes.NormalSet),
            MatchWinnerTypes.NotDefined,
        )


class BracketMathTests(unittest.TestCase):
    def test_ceil_power_of_two(self):
        self.assertEqual(tnh.CeilPowerOfTwo(1), 1)
        self.assertEqual(tnh.CeilPowerOfTwo(2), 2)
        self.assertEqual(tnh.CeilPowerOfTwo(3), 4)
        self.assertEqual(tnh.CeilPowerOfTwo(5), 8)
        self.assertEqual(tnh.CeilPowerOfTwo(8), 8)

    def test_get_tournament_stage(self):
        self.assertIsNone(tnh.GetTournamentStage(1))
        self.assertEqual(tnh.GetTournamentStage(2), 1)
        self.assertEqual(tnh.GetTournamentStage(4), 2)
        self.assertEqual(tnh.GetTournamentStage(5), 4)
        self.assertEqual(tnh.GetTournamentStage(8), 4)

    def test_delete_extra_seeds(self):
        self.assertEqual(
            tnh.DeleteExtraSeeds([(1, 8), (5, 4), (3, 6), (7, 2)], 4),
            [(1, None), (None, 4), (3, None), (None, 2)],
        )

    def test_get_seeds_positions(self):
        self.assertEqual(tnh.GetSeedsPositions(4, 2), [(1, None), (None, 2)])
        self.assertEqual(
            tnh.GetSeedsPositions(8, 4),
            [(1, None), (None, 4), (3, None), (None, 2)],
        )

    def test_get_set_games(self):
        self.assertEqual(tnh.GetSetGames(SetTypes.NormalSet), 6)
        self.assertEqual(tnh.GetSetGames(SetTypes.ShortSet), 4)
        self.assertEqual(tnh.GetSetGames(SetTypes.LongSet), 8)
        self.assertEqual(tnh.GetSetGames(SetTypes.MatchTieBreak), 10)


class ClassificationTests(unittest.TestCase):
    def _match(self, n1, n2, score, sets=1, lastSetType=SetTypes.NormalSet):
        return Match(
            Player(n1), Player(n2), score=score, scoreType=ScoreTypes.Normal,
            sets=sets, setType=SetTypes.NormalSet, lastSetType=lastSetType,
            isTeam1Set=True, isTeam2Set=True,
        )

    def test_get_teams_from_matches(self):
        matches = [self._match("A", "B", [(6, 0)]), self._match("A", "C", [(6, 1)])]
        names = {t.name for t in tnh.GetTeamsFromMatches(matches)}
        self.assertEqual(names, {"A", "B", "C"})

    def test_get_match_balances(self):
        def test(score, sets, setBalanceResult, gameBalanceResult, lastSetType=SetTypes.NormalSet):
            m = self._match("A", "B", score, sets, lastSetType)
            self.assertEqual(tnh.GetMatchBalances(m), (setBalanceResult, gameBalanceResult))

        test([(6,4)], 1,  1,  2)
        test([(1,6)], 1, -1, -5)
        test([(6,3), (6,4)], 3,  2,  5)
        test([(0,6), (6,7)], 3, -2, -7)
        test([(0,6), (6,0), (10,5)],  3,  1, 0, SetTypes.MatchTieBreak)
        test([(7,5), (6,7), (10,12)], 3, -1, 1, SetTypes.MatchTieBreak)
        test([(7,5), (6,7), (6,1)], 3,  1,  6)
        test([(6,1), (1,6), (3,6)], 3, -1, -3)

    def test_match_balances_zero_when_no_winner(self):
        m = Match(Player("A"), Player("B"), sets=1)  # sem placar
        self.assertEqual(tnh.GetMatchBalances(m), (0, 0))

    def test_get_classification_orders_and_detects_completion(self):
        matches = [
            self._match("A", "B", [(6, 0)]),
            self._match("A", "C", [(6, 1)]),
            self._match("B", "C", [(6, 2)]),
        ]
        classification, isFinal = tnh.GetClassification(matches)
        self.assertTrue(isFinal)
        self.assertEqual(list(classification.keys())[0], "A")  # 2 vitórias
        self.assertEqual(classification["A"]["Victories"], 2)

    def test_classification_incomplete(self):
        matches = [
            self._match("A", "B", [(6, 0)]),
            Match(Player("A"), Player("C"), sets=1, isTeam1Set=True, isTeam2Set=True),
        ]
        _, isFinal = tnh.GetClassification(matches)
        self.assertFalse(isFinal)


class SortingTests(unittest.TestCase):
    def test_sort_classification(self):
        data = {
            "A": {"Victories": 1, "SetBalance": 0, "GameBalance": 0},
            "B": {"Victories": 2, "SetBalance": 0, "GameBalance": 0},
            "C": {"Victories": 1, "SetBalance": 1, "GameBalance": 0},
        }
        self.assertEqual(list(tnh.SortClassification(data).keys()), ["B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
