import os
import pandas as pd
import tempfile
import unittest

from tennis_manager.category import Category
from tennis_manager.matchTeams import Player
from tennis_manager.ranking import Ranking, RankingColumns
from tennis_manager.rankingHtmlExporter import ExportToHtml as ExportRankingToHtml
from tennis_manager.tennisEnums import CategoryTypes
from tennis_manager.tournament import Tournament


class RankingHtmlExporterTests(unittest.TestCase):
  def BuildRanking(self):
    rows = [
      ["A", 1, "Ana", 30, 2, 10, 12, 10],
      ["A", 2, "Bia", 26, 1, 8, 9, 10],
      ["A", 3, "Clara", 20, 0, 6, 6, 8],
      ["A", 4, "Duda", 18, 0, 6, 4, 8],
      ["A", 5, "Eva", 15, 0, 3, 4, 8],
      ["A", 6, "Fabi", 10, 0, 3, 3, 4],
      ["B", 1, "Gabi", 12, 0, 4, 4, 4],
    ]
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

    tournament = Tournament("Etapa Teste")
    categoryA = Category("A", CategoryTypes.SingleElimination)
    categoryB = Category("B", CategoryTypes.SingleElimination)
    for name in ["Ana", "Bia", "Clara"]:
      categoryA.AddTeam(Player(name))
    for name in ["Gabi", "Helena"]:
      categoryB.AddTeam(Player(name))
    tournament.AddCategory(categoryA)
    tournament.AddCategory(categoryB)

    ranking = Ranking("Ranking Teste", [])
    ranking.data = pd.DataFrame(rows, columns=columns)
    ranking.tournaments[tournament.name] = tournament
    return ranking


  def ExportRanking(self):
    ranking = self.BuildRanking()
    with tempfile.TemporaryDirectory() as tempDir:
      filePath = os.path.join(tempDir, "ranking.html")
      ExportRankingToHtml(ranking, filePath)
      with open(filePath, encoding="utf-8") as file:
        return file.read()


  def test_export_starts_with_only_top_five_visible_and_expand_button(self):
    html = self.ExportRanking()

    self.assertIn("Ver classificacao completa", html)
    self.assertIn('type="checkbox"', html)
    self.assertIn('class="category-toggle"', html)
    self.assertIn('class="toggle-button"', html)
    self.assertIn('data-position="6"', html)
    self.assertIn('class="ranking-row is-hidden" data-position="6"', html)
    self.assertIn("Ver apenas top 5", html)


  def test_export_includes_points_stage_discard_and_chart_data(self):
    html = self.ExportRanking()

    self.assertIn('<td class="points-cell">30</td>', html)
    self.assertIn("<th>Etapa 1</th>", html)
    self.assertIn("<th>Etapa 2</th>", html)
    self.assertIn("<th>Etapa 3</th>", html)
    self.assertIn('<td class="discarded-value">2</td>', html)
    self.assertNotIn("Classificacao por categoria", html)
    self.assertIn('<col class="position-col">', html)
    self.assertIn('<col class="name-col">', html)
    self.assertIn('<col class="score-col">', html)
    self.assertIn("position: sticky", html)
    self.assertIn("left: 52px", html)
    self.assertIn("overflow-wrap: anywhere", html)
    self.assertIn("Inscritos por etapa", html)
    self.assertIn('class="chart-bars"', html)
    self.assertIn('class="chart-column"', html)
    self.assertIn('class="bar"', html)
    self.assertIn('class="bar-segment"', html)
    self.assertIn('title="A: 3"', html)
    self.assertIn('title="B: 2"', html)
    self.assertIn('Etapa 1', html)
    self.assertIn("category-toggle:checked ~ .table-wrap .ranking-row.is-hidden", html)
    self.assertIn("flex: 0 0 76px", html)
    self.assertNotIn("<script>", html)
    self.assertNotIn("data-chart", html)
    self.assertNotIn("JSON.parse", html)
    self.assertNotIn("classList", html)
    self.assertNotIn("flatMap", html)
    self.assertNotIn("Object.fromEntries", html)
    self.assertNotIn("=>", html)
    self.assertNotIn(".append(", html)
    self.assertNotIn("chart.dataset.chart", html)


if __name__ == "__main__":
  unittest.main()
