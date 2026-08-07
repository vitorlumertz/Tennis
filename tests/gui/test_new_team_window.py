import unittest

from Interface.newTeamWindow import GetAvailableDoublePlayers, GetPossibleDoublePartners
from tennis_manager.category import Category
from tennis_manager.matchTeams import Double, Player
from tennis_manager.tennisEnums import CategoryTypes, MatchTypes


class RandomDoubleSelectorTests(unittest.TestCase):
  def test_possible_partners_follow_seed_rule_and_exclude_defined_doubles(self):
    category = Category("C", CategoryTypes.RoundRobin, MatchTypes.Double, isRandomDoubles=True)
    for name, seed in [("A", 1), ("B", 1), ("C", 2), ("D", 2), ("E", 3), ("F", 3)]:
      category.AddTeam(Player(name, seedNumber=seed))
    category.AddTeam(Double(category.GetPlayer("A"), category.GetPlayer("F")))

    self.assertEqual(list(GetAvailableDoublePlayers(category)), ["B", "C", "D", "E"])

    for p1, p2 in [("B", "E"), ("E", "B"), ("C", "D"), ("D", "C")]:
      self.assertEqual(
        [player.name for player in GetPossibleDoublePartners(category, p1)],
        [p2],
      )


  def test_editing_double_makes_its_players_available(self):
    category = Category("C", CategoryTypes.RoundRobin, MatchTypes.Double, isRandomDoubles=True)
    for name, seed in [("A", 1), ("B", 2), ("C", 1), ("D", 2)]:
      category.AddTeam(Player(name, seedNumber=seed))
    double = Double(category.GetPlayer("A"), category.GetPlayer("B"))
    category.AddTeam(double)

    self.assertEqual(
      list(GetAvailableDoublePlayers(category, double.name)),
      ["A", "B", "C", "D"],
    )


  def test_partner_rule_uses_all_players_even_when_seed_extremes_are_unavailable(self):
    category = Category("C", CategoryTypes.RoundRobin, MatchTypes.Double, isRandomDoubles=True)
    for name, seed in [("A", 1), ("B", 1), ("C", 2), ("D", 2), ("E", 3), ("F", 3)]:
      category.AddTeam(Player(name, seedNumber=seed))
    category.AddTeam(Double(category.GetPlayer("A"), category.GetPlayer("E")))
    category.AddTeam(Double(category.GetPlayer("B"), category.GetPlayer("F")))

    self.assertEqual(
      [player.name for player in GetPossibleDoublePartners(category, "C")],
      ["D"],
    )


if __name__ == "__main__":
  unittest.main()
