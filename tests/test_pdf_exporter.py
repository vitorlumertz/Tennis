import os
import tempfile
import unittest

try:
  import reportlab  # noqa: F401
  HAS_REPORTLAB = True
except ImportError:
  HAS_REPORTLAB = False

from tennis_manager.category import Category
from tennis_manager.matchTeams import Player
from tennis_manager.tennisEnums import CategoryTypes, MatchTypes, SetTypes, ScoreTypes


def _export(cat):
  fd, path = tempfile.mkstemp(suffix=".pdf")
  os.close(fd)
  from tennis_manager.pdfExporter import ExportCategoryToPdf

  ExportCategoryToPdf(cat, path)
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

  def test_single_elimination_pdf(self):
    cat = self._build(CategoryTypes.SingleElimination, 8)
    cat.GetBracket()
    cat.CompleteMatches(sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet)
    first_match = next(iter(cat.matches.values()))
    first_match.SetScore([(6, 4)], ScoreTypes.Normal)
    self._assert_pdf(_export(cat))


if __name__ == "__main__":
  unittest.main()
