from enum import Enum
from typing import Literal, Self
from tennisHelper import GetTournamentStage


class MatchKeyType(Enum):
  RoundRobin = "RR"
  Groups = "GR"
  SingleElimination = "SE"
  NotDefined = "ND"


class MatchKey:
  def __init__(self, key:str|None=None, firstInfo:int|None=None, stageType:MatchKeyType|None=None, thirdInfo:int|None=None):
    if key:
      n = len(key)
      if n != 8:
        raise ValueError(f"Match key must have 8 characters. Given key ({key}) has ({n}).")

      self.name = key
      self.firstInfo = int(key[:3])
      self.stageType = MatchKeyType(key[3:5])
      self.thirdInfo = int(key[5:])

    else:
      self.firstInfo = self.__CheckNumInfo(firstInfo)
      self.thirdInfo = self.__CheckNumInfo(thirdInfo)

      self.stageType = stageType or MatchKeyType.NotDefined
      self.name = str(self.firstInfo).zfill(3) + self.stageType.value + str(self.thirdInfo).zfill(3)


  def __CheckNumInfo(self, n:int|None) -> int:
    if n is None:
      return 0
    if (n < 0) or (n > 999):
      raise ValueError(f"Number of match key must be between 0 and 999. {n} was provided.")
    return n


  def __str__(self):
    return self.name


  def IsRoundRobin(self) -> bool:
    return self.stageType is MatchKeyType.RoundRobin


  def IsGroups(self) -> bool:
    return self.stageType is MatchKeyType.Groups


  def IsSingleElimination(self) -> bool:
    return self.stageType is MatchKeyType.SingleElimination


  def IsSameStage(self, otherKey:Self) -> bool:
    return (self.firstInfo == otherKey.firstInfo) and (self.stageType == otherKey.stageType)


  def NextKey(self) -> tuple[Self, Literal[0,1]] | tuple[None, None]:
    if not self.IsSingleElimination():
      raise NotImplementedError

    stage = self.firstInfo
    if stage == 1:
      return (None, None)
    n = self.thirdInfo
    newStage = int(stage / 2)
    position = 1
    if n % 2 == 1:
      n += 1
      position = 0
    newN = int(n / 2)

    nextMatchKey = MatchKey(
      firstInfo = newStage,
      stageType = MatchKeyType.SingleElimination,
      thirdInfo = newN,
    )

    return nextMatchKey, position


  def GetMatchSortCriteria(self):
    if self.IsGroups():
      firstCriteria = 0
      secondCriteria = self.firstInfo
    else:
      firstCriteria = 1
      secondCriteria = 1 / self.firstInfo

    thirdCriteria = self.thirdInfo

    return((firstCriteria, secondCriteria, thirdCriteria))


def GetStageMatchKeys(numPlayers:int) -> list[MatchKey]:
  stage = GetTournamentStage(numPlayers)
  return [
    MatchKey(
      firstInfo = stage,
      stageType = MatchKeyType.SingleElimination,
      thirdInfo = n,
    )
    for n in range(1, stage + 1)
  ]