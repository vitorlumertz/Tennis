import unittest

from GoogleSheets.tournamentExport import GetStageName, GetRange, rowcol_to_fixed_a1


class StageNameTests(unittest.TestCase):
    def test_known_stages(self):
        self.assertEqual(GetStageName(1), "Final")
        self.assertEqual(GetStageName(2), "Semifinal")
        self.assertEqual(GetStageName(4), "Quartas de Final")
        self.assertEqual(GetStageName(8), "Oitavas de Final")
        self.assertEqual(GetStageName(16), "R32")

    def test_unknown_stage_raises(self):
        with self.assertRaises(Exception):
            GetStageName(3)


class A1NotationTests(unittest.TestCase):
    def test_rowcol_to_fixed_a1(self):
        self.assertEqual(rowcol_to_fixed_a1(1, 1), "A1")
        self.assertEqual(rowcol_to_fixed_a1(2, 3), "C2")
        self.assertEqual(rowcol_to_fixed_a1(1, 1, isFixed=True), "$A$1")
        self.assertEqual(rowcol_to_fixed_a1(2, 3, isFixed=True), "$C$2")

    def test_get_range_single_cell(self):
        self.assertEqual(GetRange(1, 1), "A1")

    def test_get_range_span(self):
        self.assertEqual(GetRange(1, 1, 2, 2), "A1:B2")

    def test_get_range_fixed(self):
        self.assertEqual(GetRange(1, 1, 2, 2, isFixed=True), "$A$1:$B$2")


if __name__ == "__main__":
    unittest.main()
