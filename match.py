import tennisHelper as tnh
from tennisEnums import *
from matchTeams import Double, Team


class Match:
  def __init__(
    self,
    team1: Team|None,
    team2: Team|None,
    score = None,
    scoreType = ScoreTypes.NotDefined,
    sets = 3,
    setType = SetTypes.NormalSet,
    lastSetType = SetTypes.MatchTieBreak,
    isTeamsSet = False,
  ):
    self.team1 = team1
    self.team2 = team2
    self.sets = sets
    self.setType = setType
    self.lastSetType = lastSetType
    self.isTeamsSet = isTeamsSet
    if (isinstance(self.team1, Double)) or (isinstance(self.team2, Double)):
      self.matchType = MatchTypes.Double
    else:
      self.matchType = MatchTypes.Single
    self.SetScore(score, scoreType)
    

  def SetScore(self, score=None, scoreType=ScoreTypes.Normal):
    if not self.isTeamsSet:
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
        if score is None:
          scoreType = ScoreTypes.NotDefined
          matchWinner = MatchWinnerTypes.NotDefined
        else:
          if (scoreType is ScoreTypes.Normal) or (scoreType is ScoreTypes.NotDefined):
            matchWinner = tnh.IsValidScore(score, self.sets)
            if matchWinner is MatchWinnerTypes.NotDefined:
              scoreType = ScoreTypes.Invalid
            else:
              scoreType = ScoreTypes.Normal
          elif scoreType is ScoreTypes.WO_to_T1:
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
            matchWinner = MatchWinnerTypes.Team2
          elif scoreType is ScoreTypes.T2Forfeit:
            matchWinner = MatchWinnerTypes.Team1

    self.score = score
    self.scoreType = scoreType
    self.matchWinner = matchWinner