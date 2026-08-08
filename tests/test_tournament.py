import unittest

from tennis_manager.tournament import Tournament
from tennis_manager.category import Category
from tennis_manager.classification import Columns
from tennis_manager.matchTeams import Double, Player
from tennis_manager.tennisEnums import CategoryTypes, GroupClassificationTypes, GroupDrawTypes, MatchTypes, SetTypes
from tennis_manager.tennisExceptions import CategoryNotFound, DuplicatedCategory


def empty_tournament():
  return Tournament("T", sets=1)


class TournamentBasicsTests(unittest.TestCase):
  def test_add_and_get_category(self):
    t = empty_tournament()
    cat = Category("A", CategoryTypes.RoundRobin, MatchTypes.Single)
    t.AddCategory(cat)
    self.assertIs(t.GetCategory("A"), cat)


  def test_duplicate_category_raises(self):
    t = empty_tournament()
    t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
    with self.assertRaises(DuplicatedCategory):
      t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))


  def test_get_missing_category_raises(self):
    with self.assertRaises(CategoryNotFound):
      empty_tournament().GetCategory("nope")


  def test_add_team_delegates_to_category(self):
    t = empty_tournament()
    t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
    t.AddTeam(Player("Ana"), "A")
    self.assertIn("Ana", t.GetCategory("A").teams)


  def test_add_old_double(self):
    t = empty_tournament()
    t.AddOldDouble("Ana", "Bia")
    self.assertEqual(t.oldDoubles, [("Ana", "Bia")])


  def test_repr_contains_name(self):
    self.assertIn("T", repr(empty_tournament()))


class StartCategoryTests(unittest.TestCase):
  def _tournament_with_round_robin(self):
    t = Tournament("T", sets=1)
    cat = Category("A", CategoryTypes.RoundRobin, MatchTypes.Single)
    t.AddCategory(cat)
    for i in range(4):
      t.AddTeam(Player(f"P{i}"), "A")
    return t


  def test_start_category_initializes_and_creates_matches(self):
    t = self._tournament_with_round_robin()
    t.StartCategory("A")
    cat = t.GetCategory("A")
    self.assertTrue(cat.isInitialized)
    self.assertEqual(len(cat.matches), 6)  # C(4,2)


  def test_start_category_idempotent(self):
    t = self._tournament_with_round_robin()
    t.StartCategory("A")
    n = len(t.GetCategory("A").matches)
    t.StartCategory("A")  # já iniciado -> sem efeito
    self.assertEqual(len(t.GetCategory("A").matches), n)


  def test_start_categories_all(self):
    t = self._tournament_with_round_robin()
    t.AddCategory(Category("B", CategoryTypes.RoundRobin, MatchTypes.Single))
    for i in range(3):
      t.AddTeam(Player(f"Q{i}"), "B")
    t.StartCategories()
    self.assertTrue(t.GetCategory("A").isInitialized)
    self.assertTrue(t.GetCategory("B").isInitialized)


  def test_update_brackets_runs(self):
    t = self._tournament_with_round_robin()
    t.StartCategory("A")
    t.UpdateBrackets()  # não deve lançar


class CleanCopyTests(unittest.TestCase):
  def test_copies_tournament_and_category_settings_without_competition_state(self):
    tournament = Tournament(
      "Original",
      sets=5,
      setType=SetTypes.ShortSet,
      lastSetType=SetTypes.LongSet,
      classificationCriteria=[Columns.Points, Columns.GameBalance],
      resultPoints={(3, 0): 7},
    )
    category = Category(
      "Duplas",
      CategoryTypes.Groups,
      MatchTypes.Double,
      isGroupsFinished=True,
      isRandomDoubles=True,
      isInitialized=True,
      groups=[[]],
      groupClassificationType=GroupClassificationTypes.TotalNumber,
      numOfclassifiedsInGroups=4,
      groupDrawType=GroupDrawTypes.ByNumberOfGroups,
      groupDrawQuantity=2,
    )
    category.AddTeam(Player("Ana", seedNumber=1))
    category.AddTeam(Player("Bia", seedNumber=2))
    category.matches["existing"] = object()
    category.bracket["existing"] = "Ana/Bia"
    tournament.AddCategory(category)

    copied = tournament.CleanCopy("Copia")
    copied_category = copied.GetCategory("Duplas")

    self.assertEqual(copied.name, "Copia")
    self.assertEqual(copied.sets, tournament.sets)
    self.assertIs(copied.setType, tournament.setType)
    self.assertIs(copied.lastSetType, tournament.lastSetType)
    self.assertEqual(copied.classificationCriteria, tournament.classificationCriteria)
    self.assertEqual(copied.resultPoints, tournament.resultPoints)
    self.assertIsNot(copied.classificationCriteria, tournament.classificationCriteria)
    self.assertIsNot(copied.resultPoints, tournament.resultPoints)

    self.assertIsNot(copied_category, category)
    self.assertEqual(copied_category.name, category.name)
    self.assertIs(copied_category.categoryType, category.categoryType)
    self.assertIs(copied_category.matchType, category.matchType)
    self.assertEqual(copied_category.isRandomDoubles, category.isRandomDoubles)
    self.assertIs(copied_category.groupClassificationType, category.groupClassificationType)
    self.assertEqual(copied_category.numOfclassifiedsInGroups, category.numOfclassifiedsInGroups)
    self.assertIs(copied_category.groupDrawType, category.groupDrawType)
    self.assertEqual(copied_category.groupDrawQuantity, category.groupDrawQuantity)
    self.assertFalse(copied_category.isGroupsFinished)
    self.assertFalse(copied_category.isInitialized)
    self.assertEqual(copied_category.players, {})
    self.assertEqual(copied_category.teams, {})
    self.assertIsNone(copied_category.groups)
    self.assertEqual(copied_category.matches, {})
    self.assertEqual(copied_category.bracket, {})


  def test_copies_old_doubles_and_adds_current_doubles(self):
    tournament = Tournament("Original", oldDoubles=[("Antiga 1", "Antiga 2")])
    category = Category("Duplas", CategoryTypes.RoundRobin, MatchTypes.Double)
    category.AddTeam(Double(Player("Ana"), Player("Bia")))
    category.AddTeam(Double(Player("Caio"), Player("Duda")))
    tournament.AddCategory(category)

    copied = tournament.CleanCopy("Copia")

    self.assertEqual(
      copied.oldDoubles,
      [("Antiga 1", "Antiga 2"), ("Ana", "Bia"), ("Caio", "Duda")],
    )
    self.assertIsNot(copied.oldDoubles, tournament.oldDoubles)
    self.assertEqual(copied.GetCategory("Duplas").teams, {})
    self.assertEqual(len(tournament.GetCategory("Duplas").teams), 2)


if __name__ == "__main__":
  unittest.main()
