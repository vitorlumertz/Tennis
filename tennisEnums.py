from enum import Enum


class MatchTypes(Enum):
  Single = 1
  Double = 2


class CategoryTypes(Enum):
  RoundRobin = 0
  SingleElimination = 1
  DoubleElimination = 2
  Groups = 3
  Teams = 4
  Automatic = 5


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
  Ranking = 0
  Tournament = 1
  Categories = 2
  Players = 3
  OldDoubles = 4
  Doubles = 5
  Groups = 6
  Matches = 7
  End = 8