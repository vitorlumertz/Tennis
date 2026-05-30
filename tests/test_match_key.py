import unittest
from typing import Literal

from matchKey import MatchKey, MatchKeyType, GetStageMatchKeys


class CreationByStrTests(unittest.TestCase):
  def Test(self, key:str, firstInfo:int, thirdInfo:int, type:MatchKeyType):
    mk = MatchKey(key)
    self.assertEqual(mk.firstInfo, firstInfo)
    self.assertEqual(mk.thirdInfo, thirdInfo)
    self.assertEqual(mk.stageType, type)

  def test_round_robin(self):
    self.Test("006RR002", 6, 2, MatchKeyType.RoundRobin)

  def test_groups(self):
    self.Test("002RGR003", 2, 3, MatchKeyType.Groups)

  def test_groups(self):
    self.Test("004SE001", 4, 1, MatchKeyType.SingleElimination)

  def test_not_defined(self):
    self.Test("000ND000", 0, 0, MatchKeyType.NotDefined)

  def test_length_error(self):
    with self.assertRaises(ValueError):
      MatchKey("abc")


class CreationByInfosTests(unittest.TestCase):
  def Test(self, firstInfo:int|None, thirdInfo:int|None, type:MatchKeyType|None, expectedName:str):
    mk = MatchKey(
      firstInfo = firstInfo,
      stageType = type,
      thirdInfo = thirdInfo,
    )
    self.assertEqual(mk.name, expectedName)

  def test_round_robin(self):
    self.Test(6, 3, MatchKeyType.RoundRobin, "006RR003")

  def test_groups(self):
    self.Test(999, 1, MatchKeyType.Groups, "999GR001")

  def test_single_elimination(self):
    self.Test(16, 5, MatchKeyType.SingleElimination, "016SE005")

  def test_empty_init(self):
    self.Test(None, None, None, "000ND000")

  def test_num_error(self):
    with self.assertRaises(ValueError):
      MatchKey(firstInfo = -1)
    with self.assertRaises(ValueError):
      MatchKey(thirdInfo = 1000)


class StageTests(unittest.TestCase):
  def test_is_round_robin(self):
    self.assertTrue(MatchKey("001RR001").IsRoundRobin())
    self.assertFalse(MatchKey("001GR001").IsRoundRobin())
    self.assertFalse(MatchKey("001SE001").IsRoundRobin())
    self.assertFalse(MatchKey("001ND001").IsRoundRobin())

  def test_is_groups(self):
    self.assertFalse(MatchKey("001RR001").IsGroups())
    self.assertTrue(MatchKey("001GR001").IsGroups())
    self.assertFalse(MatchKey("001SE001").IsGroups())
    self.assertFalse(MatchKey("001ND001").IsGroups())

  def test_is_single_elimination(self):
    self.assertFalse(MatchKey("001RR001").IsSingleElimination())
    self.assertFalse(MatchKey("001GR001").IsSingleElimination())
    self.assertTrue(MatchKey("001SE001").IsSingleElimination())
    self.assertFalse(MatchKey("001ND001").IsSingleElimination())


class NextKeyTests(unittest.TestCase):
  def Test(self, key:str, expectedNextKey:str|None, expectedPosition:Literal[0,1]|None):
    nextKey, position = MatchKey(key).NextKey()
    nextKeyName = nextKey.name if nextKey else None
    result = (nextKeyName, position)
    self.assertEqual(result, (expectedNextKey, expectedPosition))

  def test_get_next_match_key(self):
    self.Test("002SE001", "001SE001", 0)
    self.Test("002SE002", "001SE001", 1)
    self.Test("004SE003", "002SE002", 0)
    self.Test("004SE004", "002SE002", 1)
    self.Test("001SE001", None, None)

  def test_error(self):
    with self.assertRaises(NotImplementedError):
      MatchKey("001GR001").NextKey()


class SortCriteriaTests(unittest.TestCase):
  def Test(self, key1:str, key2:str):
    before = MatchKey(key1).GetMatchSortCriteria()
    after  = MatchKey(key2).GetMatchSortCriteria()
    self.assertLess(before, after)

  def test_group_before_elimination(self):
    self.Test("001GR001", "004SE001")

  def test_elimination_order(self):
    self.Test("004SE001", "001SE001")

  def test_group(self):
    self.Test("001GR003", "003GR001")
    self.Test("003GR001", "003GR002")

  def test_round_robin(self):
    self.Test("006RR004", "006RR005")


class GetStageMatchKeysTests(unittest.TestCase):
  def Test(self, stage:int, expectedKeys:list[str]):
    self.assertEqual([mk.name for mk in GetStageMatchKeys(stage)],expectedKeys)

  def test_get_stage_match_keys(self):
    self.Test(4, ["002SE001", "002SE002"])
    self.Test(8, ["004SE001", "004SE002", "004SE003", "004SE004"])


if __name__ == "__main__":
  unittest.main()