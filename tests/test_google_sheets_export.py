import unittest

from tournament import Tournament
from category import Category
from tennisEnums import CategoryTypes

from GoogleSheets.tournamentExport import GetStageName, GetRange, rowcol_to_fixed_a1, ExportEliminatoryStage


class GoogleSheetsConnMock:
    def __init__(self):
        self.cells = []
        self.calledAddWorkSheet = False

    def AddWorkSheet(self, name):
        self.calledAddWorkSheet = True

    def WriteInWorkSheet(self, workSheetName, cellsRange, values, isFormula=False):
        for row in values:
            for cell in row:
                self.cells.append(cell)


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


class ExportEliminatoryStageTests(unittest.TestCase):
    def test_normal_export(self):
        t = Tournament("T", sets=1)
        t.AddCategory(Category("RR", CategoryTypes.RoundRobin))
        t.AddCategory(Category("GR", CategoryTypes.Groups))
        t.AddCategory(Category("SE", CategoryTypes.SingleElimination))

        conn = GoogleSheetsConnMock()

        ExportEliminatoryStage(t, conn, {"GR":2, "SE":4})

        self.assertTrue(conn.calledAddWorkSheet)

        self.assertNotIn("Categoria RR", conn.cells)
        self.assertIn("Categoria GR", conn.cells)
        self.assertIn("Categoria SE", conn.cells)

        self.assertIn("Quartas de Final", conn.cells)
        self.assertIn("Semifinal", conn.cells)
        self.assertIn("Final", conn.cells)
        self.assertNotIn("Oitavas de Final", conn.cells)

    def test_pass_worksheet_creation(self):
        t = Tournament("T", sets=1)
        t.AddCategory(Category("RR", CategoryTypes.RoundRobin))
        conn = GoogleSheetsConnMock()

        ExportEliminatoryStage(t, conn, {"RR":2})

        self.assertEqual(len(conn.cells), 0)
        self.assertFalse(conn.calledAddWorkSheet)

    def test_no_initial_stage_defined_error(self):
        t = Tournament("T", sets=1)
        t.AddCategory(Category("GR", CategoryTypes.Groups))
        conn = GoogleSheetsConnMock()

        with self.assertRaises(Exception):
            ExportEliminatoryStage(t, conn, {})


if __name__ == "__main__":
    unittest.main()
