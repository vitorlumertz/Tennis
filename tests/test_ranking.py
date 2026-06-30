import pandas as pd
import unittest

from tennis_manager.ranking import Ranking, RankingColumns


class RankingTests(unittest.TestCase):
  def BuildRanking(self, rows):
    columns = [
      RankingColumns.Category.name,
      RankingColumns.Position.name,
      RankingColumns.Name.name,
      RankingColumns.Points.name,
      RankingColumns.DiscardedValue.name,
      "1",
      "2",
      "3",
    ]

    ranking = Ranking("Ranking", [])
    ranking.data = pd.DataFrame(rows, columns=columns)
    ranking._Ranking__UpdatePositions()
    return ranking


  def test_position_uses_best_stage_point_counts_as_tie_breaker(self):
    ranking = self.BuildRanking([
      ["A", None, "Ana", 11, 0, 8, 3, 0],
      ["A", None, "Bia", 11, 0, 8, 2, 1],
      ["A", None, "Clara", 11, 0, 10, 1, 0],
    ])

    self.assertEqual(
      ranking.data[RankingColumns.Name.name].tolist(),
      ["Clara", "Ana", "Bia"],
    )
    self.assertEqual(
      ranking.data[RankingColumns.Position.name].tolist(),
      [1, 2, 3],
    )


  def test_position_remains_tied_when_stage_point_counts_are_equal(self):
    ranking = self.BuildRanking([
      ["A", None, "Ana", 11, 0, 8, 3, 0],
      ["A", None, "Bia", 11, 0, 3, 8, 0],
      ["A", None, "Clara", 10, 0, 10, 0, 0],
    ])

    self.assertEqual(
      ranking.data[RankingColumns.Name.name].tolist(),
      ["Ana", "Bia", "Clara"],
    )
    self.assertEqual(
      ranking.data[RankingColumns.Position.name].tolist(),
      [1, 1, 3],
    )


if __name__ == "__main__":
  unittest.main()
