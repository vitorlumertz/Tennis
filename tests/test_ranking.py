import pandas as pd
import unittest

from tennis_manager.category import Category
from tennis_manager.matchTeams import Double, Player
from tennis_manager.ranking import Ranking, RankingColumns
from tennis_manager.tennisEnums import CategoryTypes, MatchTypes, ScoreTypes
from tennis_manager.tournament import Tournament


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


  def BuildCompleteEliminationTournament(self):
    tournament = Tournament("Etapa Eliminatoria", sets=1)
    category = Category("Simples A", CategoryTypes.SingleElimination, MatchTypes.Single)
    tournament.AddCategory(category)

    for seedNumber, name in enumerate(["Ana", "Clara", "Bia", "Duda"], start=1):
      tournament.AddTeam(Player(name, seedNumber=seedNumber), category.name)

    tournament.StartCategory(category.name)

    while True:
      updated = False
      for match in category.matches.values():
        if (
          match.matchKey.IsSingleElimination()
          and match.IsTeamsSet()
          and match.team1 is not None
          and match.team2 is not None
          and match.scoreType is ScoreTypes.NotDefined
        ):
          match.SetScore([(6, 0)], ScoreTypes.Normal)
          updated = True

      if not updated:
        break

      tournament.UpdateBrackets()

    return tournament


  def BuildCompleteDoublesEliminationTournament(self, name="Etapa Duplas"):
    tournament = Tournament(name, sets=1)
    category = Category("Duplas B", CategoryTypes.SingleElimination, MatchTypes.Double)
    doubles = [
      Double(Player("Ana"), Player("Bia"), seedNumber=1),
      Double(Player("Clara"), Player("Duda"), seedNumber=2),
      Double(Player("Eva"), Player("Fabi"), seedNumber=3),
      Double(Player("Gabi"), Player("Helena"), seedNumber=4),
    ]

    tournament.AddCategory(category)
    for double in doubles:
      tournament.AddTeam(double, category.name)

    tournament.StartCategory(category.name)

    while True:
      updated = False
      for match in category.matches.values():
        if (
          match.matchKey.IsSingleElimination()
          and match.IsTeamsSet()
          and match.team1 is not None
          and match.team2 is not None
          and match.scoreType is ScoreTypes.NotDefined
        ):
          match.SetScore([(6, 0)], ScoreTypes.Normal)
          updated = True

      if not updated:
        break

      tournament.UpdateBrackets()

    return tournament


  def GetRankingRows(self, ranking:Ranking):
    columns = [
      RankingColumns.Category.name,
      RankingColumns.Position.name,
      RankingColumns.Name.name,
      RankingColumns.Points.name,
      RankingColumns.DiscardedValue.name,
    ]
    return ranking.data[columns].values.tolist()


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


  def test_position_ignores_the_stage_where_each_score_was_obtained(self):
    ranking = self.BuildRanking([
      ["A", None, "Ana", 1, 0, 1, 0, 0],
      ["A", None, "Bia", 1 , 0, 0, 1, 0],
      ["A", None, "Clara", 1 , 0, 0, 0, 1],
      ["A", None, "Daiana", 16, 0, 10, 6, 0],
      ["A", None, "Elena", 16, 0, 6, 10, 0],
      ["A", None, "Fabiana", 16, 0, 8, 8, 0],
    ])

    self.assertEqual(
      ranking.data[RankingColumns.Position.name].tolist(),
      [1, 1, 3, 4, 4, 4],
    )


  def test_add_complete_elimination_tournament_scores_players_by_stage(self):
    tournament = self.BuildCompleteEliminationTournament()

    ranking = Ranking("Ranking", [tournament], discardWorstValue=False)

    self.assertEqual(
      self.GetRankingRows(ranking),
      [
        ["Simples A", 1, "Ana", 10, 0],
        ["Simples A", 2, "Clara", 8, 0],
        ["Simples A", 3, "Bia", 6, 0],
        ["Simples A", 3, "Duda", 6, 0],
      ],
    )


  def test_individual_ranking_splits_doubles_points_between_players(self):
    tournament = self.BuildCompleteDoublesEliminationTournament()

    ranking = Ranking("Ranking", [tournament], isIndividual=True, discardWorstValue=False)

    self.assertEqual(
      self.GetRankingRows(ranking),
      [
        ["Duplas B", 1, "Ana", 10, 0],
        ["Duplas B", 1, "Bia", 10, 0],
        ["Duplas B", 3, "Clara", 8, 0],
        ["Duplas B", 3, "Duda", 8, 0],
        ["Duplas B", 5, "Eva", 6, 0],
        ["Duplas B", 5, "Fabi", 6, 0],
        ["Duplas B", 5, "Gabi", 6, 0],
        ["Duplas B", 5, "Helena", 6, 0],
      ],
    )


  def test_doubles_ranking_keeps_pair_names(self):
    tournament = self.BuildCompleteDoublesEliminationTournament()

    ranking = Ranking("Ranking", [tournament], isIndividual=False, discardWorstValue=False)

    self.assertEqual(
      self.GetRankingRows(ranking),
      [
        ["Duplas B", 1, "Ana/Bia", 10, 0],
        ["Duplas B", 2, "Clara/Duda", 8, 0],
        ["Duplas B", 3, "Eva/Fabi", 6, 0],
        ["Duplas B", 3, "Gabi/Helena", 6, 0],
      ],
    )


  def test_discard_worst_value_after_multiple_complete_tournaments(self):
    tournaments = [
      self.BuildCompleteDoublesEliminationTournament("Etapa 1"),
      self.BuildCompleteDoublesEliminationTournament("Etapa 2"),
    ]

    ranking = Ranking("Ranking", tournaments, isIndividual=False)

    self.assertEqual(
      self.GetRankingRows(ranking),
      [
        ["Duplas B", 1, "Ana/Bia", 10, 10],
        ["Duplas B", 2, "Clara/Duda", 8, 8],
        ["Duplas B", 3, "Eva/Fabi", 6, 6],
        ["Duplas B", 3, "Gabi/Helena", 6, 6],
      ],
    )


if __name__ == "__main__":
  unittest.main()
