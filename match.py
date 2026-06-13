from typing import Literal
import tennisHelper as tnh
from tennisEnums import *
from tennisExceptions import ForfeitWithNoResultError
from matchTeams import Double, Team
from matchKey import MatchKey


class Match:
  def __init__(
    self,
    team1: Team|None,
    team2: Team|None,
    score: list[tuple[int, int]] | None = None,
    scoreType = ScoreTypes.NotDefined,
    sets: Literal[1, 3, 5] = 3,
    setType = SetTypes.NormalSet,
    lastSetType = SetTypes.MatchTieBreak,
    isTeam1Set = False,
    isTeam2Set = False,
    matchKey: MatchKey|None = None,
  ):
    self.team1 = team1
    self.team2 = team2

    if sets not in [1, 3, 5]:
      raise ValueError(f"Sets must be 1, 3 or 5. {sets} was given.")

    self.sets = sets
    self.setType = setType
    self.lastSetType = lastSetType
    self.isTeam1Set = isTeam1Set if team1 is None else True
    self.isTeam2Set = isTeam2Set if team2 is None else True
    self.matchKey = matchKey or MatchKey()

    if (isinstance(self.team1, Double)) or (isinstance(self.team2, Double)):
      self.matchType = MatchTypes.Double
    else:
      self.matchType = MatchTypes.Single
    self.SetScore(score, scoreType)


  def IsTeamsSet(self) -> bool:
    return self.isTeam1Set and self.isTeam2Set


  def SetTeam(self, teamNumber:int, team:Team|None):
    if teamNumber == 1:
      self.isTeam1Set = True
      self.team1 = team
    elif teamNumber == 2:
      self.isTeam2Set = True
      self.team2 = team


  def SetScore(self, score=None, scoreType=ScoreTypes.Normal):
    if not self.IsTeamsSet():
      score = None
      scoreType = ScoreTypes.NotDefined
      matchWinner = MatchWinnerTypes.NotDefined
    else:
      if (self.team1 is None) and (self.team2 is None):
        scoreType = ScoreTypes.DoubleBye
        matchWinner = MatchWinnerTypes.kNone
        score = None
      elif self.team1 is None:
        scoreType = ScoreTypes.Bye_to_T2
        matchWinner = MatchWinnerTypes.Team2
        score = None
      elif self.team2 is None:
        scoreType = ScoreTypes.Bye_to_T1
        matchWinner = MatchWinnerTypes.Team1
        score = None
      else:
        if scoreType is ScoreTypes.WO_to_T1:
          matchWinner = MatchWinnerTypes.Team1
          n = tnh.GetSetGames(self.setType)
          score = [(n,0)] * int((self.sets+1) / 2)
        elif scoreType is ScoreTypes.WO_to_T2:
          matchWinner = MatchWinnerTypes.Team2
          n = tnh.GetSetGames(self.setType)
          score = [(0,n)] * int((self.sets+1) / 2)
        elif scoreType is ScoreTypes.DoubleWO:
          matchWinner = MatchWinnerTypes.kNone
          score = None
        elif scoreType is ScoreTypes.T1Forfeit:
          if score is None:
            raise ForfeitWithNoResultError()
          matchWinner = MatchWinnerTypes.Team2
        elif scoreType is ScoreTypes.T2Forfeit:
          if score is None:
            raise ForfeitWithNoResultError()
          matchWinner = MatchWinnerTypes.Team1
        elif score is None:
          scoreType = ScoreTypes.NotDefined
          matchWinner = MatchWinnerTypes.NotDefined
        else:
          if (scoreType is ScoreTypes.Normal) or (scoreType is ScoreTypes.NotDefined):
            matchWinner = tnh.IsValidScore(score, self.sets, self.setType, self.lastSetType)
            if matchWinner is MatchWinnerTypes.NotDefined:
              scoreType = ScoreTypes.Invalid
            else:
              scoreType = ScoreTypes.Normal

    self.score = score
    self.scoreType = scoreType
    self.matchWinner = matchWinner


  def PrintScore(self) -> str:
    if self.scoreType == ScoreTypes.NotDefined:
      return '-'
    if self.scoreType != ScoreTypes.Normal:
      return self.scoreType.name
    scoreStr = ''
    for i, set in enumerate(self.score):
      if i > 0:
        scoreStr += ' '
      scoreStr += f'{set[0]}x{set[1]}'
    return scoreStr


  def GetSetType(self, setIndex:int) -> SetTypes:
    return tnh.GetSetType(setIndex, self.sets, self.setType, self.lastSetType)