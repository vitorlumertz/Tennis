import os
import tempfile
import unittest

import tennis_manager.fileReader as fr
from tennis_manager.category import Category
from tennis_manager.fileSave import SaveFile
from tennis_manager.matchTeams import Player
from tennis_manager.tournament import Tournament
from tennis_manager.classification import DEFAULT_CLASSIFICATION_CRITERIA
from tennis_manager.tennisEnums import SetTypes, CategoryTypes, MatchTypes, ScoreTypes, GroupDrawTypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "TestData", "TournamentExample1.txt")


class ParserHelpersTests(unittest.TestCase):
    def test_get_score(self):
        self.assertEqual(fr.GetScore("6x4 3x6"), [(6, 4), (3, 6)])
        self.assertIsNone(fr.GetScore(""))

    def test_get_set_type(self):
        self.assertEqual(fr.GetSetType("Normal Set"), SetTypes.NormalSet)
        self.assertEqual(fr.GetSetType("MatchTieBreak"), SetTypes.MatchTieBreak)
        self.assertEqual(fr.GetSetType("???"), SetTypes.NotDefined)

    def test_get_category_type(self):
        self.assertEqual(fr.GetCategoryType("SingleElimination"), CategoryTypes.SingleElimination)
        self.assertEqual(fr.GetCategoryType("RoundRobin"), CategoryTypes.RoundRobin)

    def test_get_match_type(self):
        self.assertEqual(fr.GetMatchType("Single"), MatchTypes.Single)
        self.assertEqual(fr.GetMatchType("Double"), MatchTypes.Double)

    def test_get_group_draw_type(self):
        self.assertEqual(fr.GetGroupDrawType("ByGroupSize"), GroupDrawTypes.ByGroupSize)
        self.assertEqual(fr.GetGroupDrawType("ByNumberOfGroups"), GroupDrawTypes.ByNumberOfGroups)

    def test_get_score_type(self):
        self.assertEqual(fr.GetScoreType("WO_to_T1"), ScoreTypes.WO_to_T1)
        self.assertEqual(fr.GetScoreType("unknown"), ScoreTypes.NotDefined)

    def test_get_boolean(self):
        self.assertTrue(fr.GetBoolean("True"))
        self.assertFalse(fr.GetBoolean("false"))


class ReadExampleTests(unittest.TestCase):
    def setUp(self):
        self.tournament = fr.ReadInputFile(EXAMPLE)

    def test_tournament_header(self):
        self.assertEqual(self.tournament.name, "Torneio Exemplo")
        self.assertEqual(self.tournament.sets, 1)
        self.assertEqual(self.tournament.setType, SetTypes.NormalSet)
        self.assertEqual(self.tournament.lastSetType, SetTypes.MatchTieBreak)
        self.assertEqual(self.tournament.classificationCriteria, DEFAULT_CLASSIFICATION_CRITERIA)

    def test_categories_loaded(self):
        self.assertEqual(len(self.tournament.categories), 4)
        self.assertIn("1a Classe Simples", self.tournament.categories)

    def test_players_loaded(self):
        cat = self.tournament.GetCategory("1a Classe Simples")
        self.assertEqual(len(cat.teams), 8)

    def test_groups_loaded(self):
        cat = self.tournament.GetCategory("2a Classe Simples")
        self.assertIsNotNone(cat.groups)
        self.assertEqual(len(cat.groups), 2)
        self.assertEqual(cat.groupDrawType, GroupDrawTypes.ByGroupSize)
        self.assertEqual(cat.groupDrawQuantity, 3)


class RoundTripTests(unittest.TestCase):
    def test_save_and_reread_preserves_structure(self):
        original = fr.ReadInputFile(EXAMPLE)
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            SaveFile(path, original)
            reloaded = fr.ReadInputFile(path)
        finally:
            os.remove(path)

        self.assertEqual(reloaded.name, original.name)
        self.assertEqual(reloaded.classificationCriteria, original.classificationCriteria)
        self.assertEqual(
            sorted(reloaded.categories), sorted(original.categories)
        )
        for name in original.categories:
            self.assertEqual(
                len(reloaded.GetCategory(name).teams),
                len(original.GetCategory(name).teams),
                f"contagem de times diferente em {name}",
            )
            self.assertEqual(
                reloaded.GetCategory(name).groupDrawType,
                original.GetCategory(name).groupDrawType,
            )
            self.assertEqual(
                reloaded.GetCategory(name).groupDrawQuantity,
                original.GetCategory(name).groupDrawQuantity,
            )

    def test_save_and_reread_preserves_custom_group_draw_settings(self):
        tournament = Tournament("T")
        category = Category(
            "C",
            CategoryTypes.Groups,
            MatchTypes.Single,
            groupDrawType=GroupDrawTypes.ByNumberOfGroups,
            groupDrawQuantity=3,
        )
        for i in range(1, 11):
            category.AddTeam(Player(f"P{i:02d}"))
        tournament.AddCategory(category)

        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            SaveFile(path, tournament)
            reloaded = fr.ReadInputFile(path)
        finally:
            os.remove(path)

        reloaded_category = reloaded.GetCategory("C")
        self.assertEqual(reloaded_category.groupDrawType, GroupDrawTypes.ByNumberOfGroups)
        self.assertEqual(reloaded_category.groupDrawQuantity, 3)


if __name__ == "__main__":
    unittest.main()
