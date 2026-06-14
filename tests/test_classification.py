import pandas as pd
import unittest

from classification import (
  Classification,
  Columns,
  MatchScoreData,
  OrderDf,
  ClassificationCriteriaToString,
  ParseClassificationCriteria,
  DEFAULT_CLASSIFICATION_CRITERIA,
)

from matchTeams import Team
from match import Match
from tennisEnums import SetTypes


class OrderDfTests(unittest.TestCase):
  def test_order_by_victories_descending(self):
    df = pd.DataFrame(
      {
        Columns.Name.name: ["A", "B", "C"],
        Columns.Victories.name: [1, 3, 2],
      }
    )

    ordered = OrderDf(df, [Columns.Victories])

    self.assertEqual(
      ordered[Columns.Victories.name].tolist(),
      [3, 2, 1]
    )
    self.assertEqual(
      ordered[Columns.Name.name].tolist(),
      ["B", "C", "A"]
    )

  def test_order_by_position_ascending(self):
    df = pd.DataFrame(
      {
        Columns.Position.name: [3, 1, 2],
      }
    )

    ordered = OrderDf(df)

    self.assertEqual(
      ordered[Columns.Position.name].tolist(),
      [1, 2, 3]
    )


  def test_order_by_multiple_columns(self):
    df = pd.DataFrame(
      {
        Columns.Name.name: ["A", "B", "C", "D", "E", "F"],
        Columns.Victories.name:   [2, 3, 3,  2,   1,   1],
        Columns.SetBalance.name:  [5, 8, 9, -6,  -3,  -3],
        Columns.GameBalance.name: [3, 8, 9,  3, -17, -10],
      }
    )

    ordered = OrderDf(df, [Columns.Victories, Columns.SetBalance, Columns.GameBalance])

    self.assertEqual(
      ordered[Columns.Name.name].tolist(),
      ["C", "B", "A", "D", "F", "E"]
    )


class MatchScoreDataTests(unittest.TestCase):
  def Test(self, score, sets, setType, lastSetType, expecteed:MatchScoreData):
    team1 = Team("A")
    team2 = Team("B")

    match = Match(
      team1,
      team2,
      score = score,
      sets = sets,
      setType = setType,
      lastSetType = lastSetType,
    )

    classification = Classification([match], [Columns.Victories])
    self.assertEqual(classification._Classification__GetMatchScoreData(match), expecteed)


  def test_match_score_data(self):
    self.Test(
      [
        (6, 4),
        (3, 6),
        (10, 8),
      ],
      3,
      SetTypes.NormalSet,
      SetTypes.MatchTieBreak,
      MatchScoreData(2, 1, 2, 1, 9, 10, 1, -1, -1, 1),
    )


    self.Test(
      [
        (6, 4),
        (3, 6),
        (4, 6),
      ],
      3,
      SetTypes.NormalSet,
      SetTypes.NormalSet,
      MatchScoreData(1, 2, 1, 2, 13, 16, -1, -3, 1, 3),
    )

    self.Test(
      [
        (0, 6),
        (6, 7),
      ],
      3,
      SetTypes.NormalSet,
      SetTypes.MatchTieBreak,
      MatchScoreData(0, 3, 0, 2, 6, 13, -2, -7, 2, 7),
    )

    self.Test(
      [
        (6, 4),
      ],
      1,
      SetTypes.NormalSet,
      SetTypes.MatchTieBreak,
      MatchScoreData(3, 0, 1, 0, 6, 4, 1, 2, -1, -2),
    )


  def test_no_winner(self):
    team1 = Team("A")
    team2 = Team("B")
    match = Match(team1, team2)

    classification = Classification([match], [Columns.Victories])
    self.assertEqual(classification._Classification__GetMatchScoreData(match), MatchScoreData())


def create_teams(n):
  return [Team(f'T{i+1}', i+1) for i in range(n)]


class ClassificationTests(unittest.TestCase):
  def assertColumn(self, classification:pd.DataFrame, column:Columns, expected):
    if column == Columns.Name:
      returned = classification.index
    else:
      returned = classification[column.name]

    self.assertEqual(returned.tolist(), expected)


  def test_round_robin(self):
    teams = create_teams(3)
    matches = [
      Match(
        teams[0], teams[1],
        [(6,0), (6,0)],
      ),
      Match(
        teams[0], teams[2],
        [(6,0), (6,0)],
      ),
      Match(
        teams[1], teams[2],
        [(0,6), (0,6)],
      ),
    ]
    sortColumns = [Columns.Victories]
    c = Classification(matches, sortColumns)

    self.assertFalse(c.hasGroups)
    self.assertTrue(c.isFinalized)

    self.assertColumn(c.classification, Columns.Name, ["T1", "T3", "T2"])
    self.assertColumn(c.classification, Columns.Position, [1, 2, 3])
    self.assertColumn(c.classification, Columns.Points, [6, 3, 0])
    self.assertColumn(c.classification, Columns.Victories, [2, 1, 0])
    self.assertColumn(c.classification, Columns.SetBalance, [4, 0, -4])
    self.assertColumn(c.classification, Columns.GameBalance, [24, 0, -24])
    self.assertColumn(c.classification, Columns.SetsWon, [4, 2, 0])
    self.assertColumn(c.classification, Columns.GamesWon, [24, 12, 0])
    self.assertColumn(c.classification, Columns.PlayedMatches, [2, 2, 2])


  def test_groups(self):
    teams = create_teams(6)
    groups = [
      [teams[0], teams[1], teams[2]],
      [teams[3], teams[4], teams[5]],
    ]
    matches = [
      Match(
        teams[0], teams[1],
        [(6,0), (6,0)],
      ),
      Match(
        teams[0], teams[2],
        [(6,7), (7,6), (2,10)],
      ),
      Match(
        teams[1], teams[2],
        [(6,3), (6,3)],
      ),
      Match(
        teams[3], teams[4],
        [(6,0), (6,0)],
      ),
      Match(
        teams[3], teams[5],
        [(0,6), (0,6)],
      ),
      Match(
        teams[4], teams[5],
        [(6,0), (6,0)],
      ),
    ]

    sortColumns = [Columns.Victories, Columns.SetBalance, Columns.GameBalance]
    c = Classification(matches, sortColumns, groups)

    self.assertTrue(c.hasGroups)
    self.assertTrue(c.isFinalized)

    self.assertColumn(c.classification, Columns.Position, [1, 2, 3, 4, 5, 6])
    self.assertColumn(c.classification, Columns.GroupPosition, [1, 1, 2, 2, 3, 3])
    self.assertColumn(c.classification, Columns.Group, [1, 2, 2, 1, 2, 1])
    self.assertEqual(c.classification.at["T1", Columns.Points.name], 4)
    self.assertEqual(c.classification.at["T2", Columns.Points.name], 3)
    self.assertEqual(c.classification.at["T3", Columns.Points.name], 2)
    self.assertEqual(c.classification.at["T4", Columns.Points.name], 3)
    self.assertEqual(c.classification.at["T5", Columns.Points.name], 3)
    self.assertEqual(c.classification.at["T6", Columns.Points.name], 3)
    self.assertColumn(c.classification, Columns.Victories, [1, 1, 1, 1, 1, 1])
    self.assertColumn(c.classification, Columns.SetBalance, [1, 0, 0, 0, 0, -1])
    self.assertColumn(c.classification, Columns.GameBalance, [12, 0, 0, -6, 0, -6])
    self.assertColumn(c.classification, Columns.SetsWon, [3, 2, 2, 2, 2, 2])
    self.assertColumn(c.classification, Columns.GamesWon, [25, 12, 12, 12, 12, 19])
    self.assertColumn(c.classification, Columns.PlayedMatches, [2, 2, 2, 2, 2, 2])

    tieDraw = c.classification[Columns.TieDraw.name].tolist()
    self.assertGreater(tieDraw[1], tieDraw[2])
    self.assertGreater(tieDraw[2], tieDraw[4])


  def test_direct_match_breaks_tie_after_previous_criteria(self):
    teams = create_teams(4)
    matches = [
      Match(
        teams[0], teams[1],
        [(6,0), (6,0)],
      ),
      Match(
        teams[0], teams[2],
        [(0,6), (0,6)],
      ),
      Match(
        teams[1], teams[3],
        [(6,0), (6,0)],
      ),
      Match(
        teams[2], teams[3],
        [(6,0), (6,0)],
      ),
    ]

    sortColumns = [Columns.Victories, Columns.SetBalance, Columns.GameBalance, Columns.DirectMatch]
    c = Classification(matches, sortColumns)

    self.assertColumn(c.classification, Columns.Name, ["T3", "T1", "T2", "T4"])
    self.assertColumn(c.classification, Columns.Victories, [2, 1, 1, 0])
    self.assertColumn(c.classification, Columns.SetBalance, [4, 0, 0, -4])
    self.assertColumn(c.classification, Columns.GameBalance, [24, 0, 0, -24])
    self.assertColumn(c.classification, Columns.DirectMatch, [0, 2, 1, 0])

  def test_points_by_set_result(self):
    teams = create_teams(4)
    matches = [
      Match(
        teams[0], teams[1],
        [(6,0), (6,0)],
      ),
      Match(
        teams[2], teams[3],
        [(6,0), (0,6), (10,8)],
      ),
    ]
    sortColumns = [Columns.Points]
    c = Classification(matches, sortColumns)

    self.assertColumn(c.classification, Columns.Name, ["T1", "T3", "T4", "T2"])
    self.assertColumn(c.classification, Columns.Points, [3, 2, 1, 0])


class ClassificationCriteriaTests(unittest.TestCase):
  def test_default_criteria_round_trip(self):
    text = ClassificationCriteriaToString(DEFAULT_CLASSIFICATION_CRITERIA)
    self.assertEqual(text, "Victories/SetBalance/GameBalance/DirectMatch")
    self.assertEqual(ParseClassificationCriteria(text), DEFAULT_CLASSIFICATION_CRITERIA)

  def test_parse_rejects_duplicate(self):
    with self.assertRaises(ValueError):
      ParseClassificationCriteria("Victories/Victories")

  def test_parse_rejects_invalid(self):
    with self.assertRaises(ValueError):
      ParseClassificationCriteria("InvalidColumn")


if __name__ == "__main__":
  unittest.main()
