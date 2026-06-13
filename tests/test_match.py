import unittest

from match import Match
from matchTeams import Player, Double
from tennisEnums import SetTypes, ScoreTypes, MatchWinnerTypes, MatchTypes
from tennisExceptions import ForfeitWithNoResultError


def make(team1, team2, **kw):
    kw.setdefault("sets", 3)
    kw.setdefault("setType", SetTypes.NormalSet)
    kw.setdefault("lastSetType", SetTypes.MatchTieBreak)
    return Match(team1, team2, **kw)


class ScoreTests(unittest.TestCase):
    def test_normal_valid_score(self):
        m = make(Player("A"), Player("B"), score=[(6, 4), (6, 3)], scoreType=ScoreTypes.Normal)
        self.assertEqual(m.scoreType, ScoreTypes.Normal)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team1)
        self.assertEqual(m.PrintScore(), "6x4 6x3")

    def test_tie_break_decider_valid(self):
        m = make(Player("A"), Player("B"), score=[(6, 4), (3, 6), (10, 8)], scoreType=ScoreTypes.Normal)
        self.assertEqual(m.scoreType, ScoreTypes.Normal)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team1)

    def test_invalid_score(self):
        m = make(Player("A"), Player("B"), score=[(6, 4), (6, 5)], scoreType=ScoreTypes.Normal)
        self.assertEqual(m.scoreType, ScoreTypes.Invalid)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.NotDefined)
        self.assertEqual(m.PrintScore(), "Invalid")

    def test_no_score_not_defined(self):
        m = make(Player("A"), Player("B"))
        self.assertEqual(m.scoreType, ScoreTypes.NotDefined)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.NotDefined)
        self.assertEqual(m.PrintScore(), "-")


class WalkoverAndForfeitTests(unittest.TestCase):
    def test_wo_to_t1(self):
        m = make(Player("A"), Player("B"), scoreType=ScoreTypes.WO_to_T1)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team1)
        self.assertEqual(m.score, [(6, 0), (6, 0)])

    def test_wo_to_t2(self):
        m = make(Player("A"), Player("B"), scoreType=ScoreTypes.WO_to_T2)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team2)
        self.assertEqual(m.score, [(0, 6), (0, 6)])

    def test_double_wo(self):
        m = make(Player("A"), Player("B"), scoreType=ScoreTypes.DoubleWO)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.kNone)

    def test_forfeits(self):
        m1 = make(Player("A"), Player("B"), scoreType=ScoreTypes.T1Forfeit, score=[(3,3)])
        self.assertEqual(m1.matchWinner, MatchWinnerTypes.Team2)
        m2 = make(Player("A"), Player("B"), scoreType=ScoreTypes.T2Forfeit, score=[(6,2)])
        self.assertEqual(m2.matchWinner, MatchWinnerTypes.Team1)

        with self.assertRaises(ForfeitWithNoResultError):
            m3 = make(Player("A"), Player("B"), scoreType=ScoreTypes.T1Forfeit)


class ByeTests(unittest.TestCase):
    def test_bye_to_t1(self):
        m = make(Player("A"), None, isTeam1Set=True, isTeam2Set=True)
        self.assertEqual(m.scoreType, ScoreTypes.Bye_to_T1)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team1)

    def test_bye_to_t2(self):
        m = make(None, Player("B"), isTeam1Set=True, isTeam2Set=True)
        self.assertEqual(m.scoreType, ScoreTypes.Bye_to_T2)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.Team2)

    def test_double_bye(self):
        m = make(None, None, isTeam1Set=True, isTeam2Set=True)
        self.assertEqual(m.scoreType, ScoreTypes.DoubleBye)
        self.assertEqual(m.matchWinner, MatchWinnerTypes.kNone)


class StateTests(unittest.TestCase):
    def test_teams_set_when_team_present(self):
        m = make(Player("A"), Player("B"))
        self.assertTrue(m.IsTeamsSet())

    def test_set_team_marks_set(self):
        m = make(None, None)
        self.assertFalse(m.IsTeamsSet())
        m.SetTeam(1, Player("A"))
        m.SetTeam(2, Player("B"))
        self.assertTrue(m.IsTeamsSet())

    def test_match_type_double(self):
        d = Double(Player("A"), Player("B"))
        m = make(d, Double(Player("C"), Player("D")))
        self.assertEqual(m.matchType, MatchTypes.Double)

    def test_match_type_single(self):
        m = make(Player("A"), Player("B"))
        self.assertEqual(m.matchType, MatchTypes.Single)


if __name__ == "__main__":
    unittest.main()
