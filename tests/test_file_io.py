import os
import tempfile
import unittest

import fileReader as fr
from fileSave import SaveFile
from tennisEnums import SetTypes, CategoryTypes, MatchTypes, ScoreTypes

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
        self.assertEqual(
            sorted(reloaded.categories), sorted(original.categories)
        )
        for name in original.categories:
            self.assertEqual(
                len(reloaded.GetCategory(name).teams),
                len(original.GetCategory(name).teams),
                f"contagem de times diferente em {name}",
            )


if __name__ == "__main__":
    unittest.main()
