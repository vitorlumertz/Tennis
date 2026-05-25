import os
import tempfile
import unittest

try:
    import reportlab  # noqa: F401
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from category import Category
from matchTeams import Player
from tennisEnums import CategoryTypes, MatchTypes, SetTypes


def _export(cat):
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    from pdfExporter import ExportGroupCategoryToPdf

    ExportGroupCategoryToPdf(cat, path)
    return path


@unittest.skipUnless(HAS_REPORTLAB, "reportlab não instalado")
class PdfExporterTests(unittest.TestCase):
    def _build(self, ctype, n):
        cat = Category("C", ctype, MatchTypes.Single)
        for i in range(n):
            cat.AddTeam(Player(f"P{i:02d}"))
        cat.GetFirstRound(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
        return cat

    def _assert_pdf(self, path):
        try:
            self.assertTrue(os.path.getsize(path) > 0)
            with open(path, "rb") as f:
                self.assertTrue(f.read(4).startswith(b"%PDF"))
        finally:
            os.remove(path)

    def test_round_robin_pdf(self):
        cat = self._build(CategoryTypes.RoundRobin, 4)
        self._assert_pdf(_export(cat))

    def test_groups_pdf(self):
        cat = self._build(CategoryTypes.Groups, 7)
        self._assert_pdf(_export(cat))


if __name__ == "__main__":
    unittest.main()
