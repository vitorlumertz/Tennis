import unittest
from groupClassification import Team_aux, GetBracketWithTeams

# Legends:
# nG: there are n groups
# Cn: classify n teams to single elimination stage


class GroupClassificationTest(unittest.TestCase):
  def Test(self, teams, bracket):
    self.assertEqual(GetBracketWithTeams(teams), bracket)


  def test_2G_C2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
      ],
      bracket = [
        ("1G1", "1G2"),
      ]
    )


  def test_2G_C3(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("2G2", 3, 2),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("1G2", None),
      ]
    )


  def test_3G_C4_seeds_preserved(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G3", 4, 3),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("1G2", "1G3"),
      ]
    )


  def test_3G_C4_seeds_not_preserved(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G1", 4, 1),
      ],
      bracket = [
        ("1G1", "1G3"),
        ("1G2", "2G1"),
      ]
    )


  def test_3G_C5_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G1", 4, 1),
        Team_aux("2G2", 5, 2),
      ],
      bracket = [
        ("1G1", None),
        (None, "2G2"),
        ("1G2", None),
        ("2G1", "1G3"),
      ]
    )


  def test_3G_C5_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G3", 4, 3),
        Team_aux("2G2", 5, 2),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "2G3"),
        ("1G2", None),
        (None, "1G3"),
      ]
    )


  def test_3G_C6_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G3", 4, 3),
        Team_aux("2G2", 5, 2),
        Team_aux("2G1", 6, 1),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "2G3"),
        ("1G2", None),
        ("2G1", "1G3"),
      ]
    )


  def test_3G_C6_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("2G1", 4, 1),
        Team_aux("2G2", 5, 2),
        Team_aux("2G3", 6, 3),
      ],
      bracket = [
        ("1G1", None),
        ("2G3", "2G2"),
        ("1G2", None),
        ("2G1", "1G3"),
      ]
    )


  def test_4G_C4(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
      ],
      bracket = [
        ("1G1", "1G4"),
        ("1G2", "1G3"),
      ]
    )

  def test_4G_C5_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G4", 5, 4),
      ],
      bracket = [
        ("1G1", None),
        (None, "1G4"),
        ("1G2", None),
        ("2G4", "1G3"),
      ]
    )


  def test_4G_C5_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G2", 5, 2),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "1G4"),
        ("1G2", None),
        (None, "1G3"),
      ]
    )


  def test_4G_C6_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G1", 5, 1),
        Team_aux("2G2", 6, 2),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "1G4"),
        ("1G2", None),
        ("2G1", "1G3"),
      ]
    )


  def test_4G_C6_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G1", 5, 1),
        Team_aux("2G4", 6, 4),
      ],
      bracket = [
        ("1G1", None),
        (None, "1G4"),
        ("1G2", "2G4"),
        ("2G1", "1G3"),
      ]
    )

  def test_4G_C6_3(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G2", 5, 2),
        Team_aux("2G3", 6, 3),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("2G2", "1G4"),
        ("1G2", None),
        (None, "1G3"),
      ]
    )


  def test_4G_C7_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G2", 5, 2),
        Team_aux("2G3", 6, 3),
        Team_aux("2G4", 7, 4),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("2G2", "1G4"),
        ("1G2", None),
        ("2G4", "1G3"),
      ]
    )


  def test_4G_C8_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G2", 5, 2),
        Team_aux("2G3", 6, 3),
        Team_aux("2G4", 7, 4),
        Team_aux("2G1", 8, 1),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("2G2", "1G4"),
        ("1G2", "2G1"),
        ("2G4", "1G3"),
      ]
    )


  def test_4G_C8_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("2G4", 5, 4),
        Team_aux("2G3", 6, 3),
        Team_aux("2G2", 7, 2),
        Team_aux("2G1", 8, 1),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("2G3", "1G4"),
        ("1G2", "2G1"),
        ("2G4", "1G3"),
      ]
    )


  def test_5G_C5(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
      ],
      bracket = [
        ("1G1", None),
        ("1G5", "1G4"),
        ("1G2", None),
        (None, "1G3"),
      ]
    )


  def test_5G_C6(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G2", 6, 2),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("1G5", "1G4"),
        ("1G2", None),
        (None, "1G3"),
      ]
    )


  def test_5G_C8_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G1", 6, 1),
        Team_aux("2G2", 7, 2),
        Team_aux("2G3", 8, 3),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("2G2", "1G4"),
        ("1G2", "2G1"),
        ("1G5", "1G3"),
      ]
    )


  def test_5G_C8_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G5", 6, 5),
        Team_aux("2G1", 7, 1),
        Team_aux("2G4", 8, 4),
      ],
      bracket = [
        ("1G1", "2G4"),
        ("2G5", "1G3"),
        ("1G2", "2G1"),
        ("1G5", "1G4"),
      ]
    )


  def test_5G_C8_3(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G1", 6, 1),
        Team_aux("2G4", 7, 4),
        Team_aux("2G2", 8, 2),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("1G5", "1G4"),
        ("1G2", "2G4"),
        ("2G1", "1G3"),
      ]
    )

  def test_5G_C8_4(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G3", 6, 3),
        Team_aux("2G4", 7, 4),
        Team_aux("2G2", 8, 2),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("2G3", "1G4"),
        ("1G2", "2G4"),
        ("1G5", "1G3"),
      ]
    )


  def test_5G_C8_5(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G5", 6, 5),
        Team_aux("2G1", 7, 1),
        Team_aux("2G2", 8, 2),
      ],
      bracket = [
        ("1G1", "2G2"),
        ("1G5", "1G4"),
        ("1G2", "2G1"),
        ("2G5", "1G3"),
      ]
    )

  def test_5G_C10_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("2G5", 6, 5),
        Team_aux("2G1", 7, 1),
        Team_aux("2G4", 8, 4),
        Team_aux("2G3", 9, 3),
        Team_aux("2G2", 10, 2),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "2G3"),
        ("1G5", None),
        (None, "1G4"),
        ("1G2", None),
        ("2G4", "2G1"),
        ("2G5", None),
        (None, "1G3"),
      ]
    )


  def test_6G_C8_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("1G6", 6, 6),
        Team_aux("2G1", 7, 1),
        Team_aux("2G4", 8, 4),
      ],
      bracket = [
        ("1G1", "1G6"),
        ("1G5", "1G4"),
        ("1G2", "2G4"),
        ("2G1", "1G3"),
      ]
    )


  def test_6G_C8_2(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("1G6", 6, 6),
        Team_aux("2G2", 7, 2),
        Team_aux("2G3", 8, 3),
      ],
      bracket = [
        ("1G1", "2G3"),
        ("2G2", "1G4"),
        ("1G2", "1G6"),
        ("1G5", "1G3"),
      ]
    )


  def test_6G_C12_1(self):
    self.Test(
      teams = [
        Team_aux("1G1", 1, 1),
        Team_aux("1G2", 2, 2),
        Team_aux("1G3", 3, 3),
        Team_aux("1G4", 4, 4),
        Team_aux("1G5", 5, 5),
        Team_aux("1G6", 6, 6),
        Team_aux("2G1", 7, 1),
        Team_aux("2G4", 8, 4),
        Team_aux("2G3", 9, 3),
        Team_aux("2G2", 10, 2),
        Team_aux("2G5", 11, 5),
        Team_aux("2G6", 12, 6),
      ],
      bracket = [
        ("1G1", None),
        ("2G2", "2G3"),
        ("1G5", "2G6"),
        (None, "1G4"),
        ("1G2", None),
        ("2G4", "2G1"),
        ("1G6", "2G5"),
        (None, "1G3"),
      ]
    )


if __name__ == "__main__":
  unittest.main()
