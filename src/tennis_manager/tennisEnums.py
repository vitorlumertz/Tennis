from enum import Enum


class MatchTypes(Enum):
  Single = 1
  Double = 2


class CategoryTypes(Enum):
  RoundRobin = 0
  SingleElimination = 1
  Groups = 2
  Automatic = 3


class GroupClassificationTypes(Enum):
  TwoPerGroup = 0
  OnePerGroup = 1
  TwoG4_OneG3 = 2 # classify two teams in groups of 4 and one in groups of 3
  TotalNumber = 3 # define total number of teams to be classified to single elimination stage


class GroupDrawTypes(Enum):
  ByGroupSize = 0
  ByNumberOfGroups = 1


class SetTypes(Enum):
  NormalSet = 0
  ShortSet = 1
  LongSet = 2
  MatchTieBreak = 3
  NotDefined = 4


class ScoreTypes(Enum):
  Normal = 0
  WO_to_T1 = 1
  WO_to_T2 = 2
  DoubleWO = 3
  T1Forfeit = 4
  T2Forfeit = 5
  Bye_to_T1 = 6
  Bye_to_T2 = 7
  DoubleBye = 8
  NotDefined = 9
  Invalid = 10


class MatchWinnerTypes(Enum):
  kNone = 0
  Team1 = 1
  Team2 = 2
  NotDefined = 3


class FileSections(Enum):
  Tournament = 0
  Categories = 1
  Players = 2
  OldDoubles = 3
  Doubles = 4
  Groups = 5
  Matches = 6
  End = 7
