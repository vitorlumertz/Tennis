from enum import Enum
from dataclasses import dataclass
from typing import Literal
import pandas as pd
import random

from match import Match
from matchTeams import Team
from tennisEnums import MatchWinnerTypes, SetTypes
import tennisHelper as tnh


class Columns(Enum):
  Position = 1
  Name = 2
  Group = 3
  GroupPosition = 4
  Points = 5 # not implemented yet
  Victories = 6
  SetBalance = 7
  GameBalance = 8
  SetsWon = 9
  GamesWon = 10
  DirectMatch = 11
  PlayedMatches = 12
  TieDraw = 13


CLASSIFICATION_CRITERIA_OPTIONS = [
  Columns.Victories,
  Columns.SetBalance,
  Columns.GameBalance,
  Columns.DirectMatch,
  Columns.SetsWon,
  Columns.GamesWon,
  Columns.PlayedMatches,
]

DEFAULT_CLASSIFICATION_CRITERIA = [
  Columns.Victories,
  Columns.SetBalance,
  Columns.GameBalance,
  Columns.DirectMatch,
]


def ClassificationCriteriaToString(criteria: list[Columns]) -> str:
  return '/'.join(column.name for column in criteria)


def ParseClassificationCriteria(string: str) -> list[Columns]:
  normalized = string.strip()
  if normalized == '':
    return list(DEFAULT_CLASSIFICATION_CRITERIA)

  criteria = []
  for part in normalized.split('/'):
    name = part.strip().replace(' ', '')
    if name == '':
      continue
    column = next((c for c in CLASSIFICATION_CRITERIA_OPTIONS if c.name.upper() == name.upper()), None)
    if column is None:
      raise ValueError(f"Critério de classificação inválido: {part.strip()}")
    if column in criteria:
      raise ValueError(f"Critério de classificação repetido: {column.name}")
    criteria.append(column)

  if len(criteria) == 0:
    return list(DEFAULT_CLASSIFICATION_CRITERIA)

  return criteria


@dataclass
class MatchScoreData:
  setsT1: int = 0
  setsT2: int = 0
  gamesT1: int = 0
  gamesT2: int = 0
  setBalanceT1: int = 0
  gameBalanceT1: int = 0
  setBalanceT2: int = 0
  gameBalanceT2: int = 0


def OrderDf(df:pd.DataFrame, sortColumns:list[Columns]=[Columns.Position]) -> pd.DataFrame:
  kAscendigColumns = [Columns.Position, Columns.GroupPosition]
  return df.sort_values(
    by = [c.name for c in sortColumns],
    ascending = [True if c in kAscendigColumns else False for c in sortColumns],
  )


class Classification:
  def __init__(self, matches:list[Match], sortColumns:list[Columns], groups:list[list[Team]]|None=None):
    self.matches = matches
    self.isFinalized = True # updated in self.__UpdateScores()

    teams = tnh.GetTeamsFromMatches(matches)

    tieDrawPoints = list(range(len(teams))) # last tie breaker criteria (draw for tied teams)
    random.shuffle(tieDrawPoints)

    classification = pd.DataFrame(
      {
        Columns.Position.name: 1,
        Columns.Name.name: team.name,
        Columns.Group.name: None,
        Columns.GroupPosition.name: None,
        Columns.Points.name: 0,
        Columns.Victories.name: 0,
        Columns.SetBalance.name: 0,
        Columns.GameBalance.name: 0,
        Columns.SetsWon.name: 0,
        Columns.GamesWon.name: 0,
        Columns.DirectMatch.name: 0,
        Columns.PlayedMatches.name: 0,
        Columns.TieDraw.name: tieDrawPoints.pop(),
      }
      for team in teams if team
    )

    classification = classification.set_index(Columns.Name.name)
    self.classification = classification

    self.__UpdateScores()

    self.hasGroups = False if groups is None else True
    if self.hasGroups:
      self.__UpdateGroups(groups)

    self.__UpdateDirectMatch(sortColumns)
    self.__UpdatePositions(sortColumns)


  @staticmethod
  def __GetMatchScoreData(match:Match) -> MatchScoreData:
    data = MatchScoreData()
    if (match.matchWinner is MatchWinnerTypes.kNone) or (match.matchWinner is MatchWinnerTypes.NotDefined):
      return data

    for i, set in enumerate(match.score):
      if set[0] > set[1]:
        data.setsT1 += 1
      else:
        data.setsT2 += 1

      if match.GetSetType(i) is not SetTypes.MatchTieBreak:
        data.gamesT1 += set[0]
        data.gamesT2 += set[1]

    data.setBalanceT1 = data.setsT1 - data.setsT2
    data.setBalanceT2 = - data.setBalanceT1

    data.gameBalanceT1 = data.gamesT1 - data.gamesT2
    data.gameBalanceT2 = - data.gameBalanceT1

    return data


  def __UpdateScore(self, team:Team, col:Columns, value:int) -> None:
    self.classification.at[team.name, col.name] += value


  def __UpdateScores(self) -> None:
    for m in self.matches:
      if m.matchWinner is MatchWinnerTypes.NotDefined:
        self.isFinalized = False
        continue

      if m.matchWinner is MatchWinnerTypes.Team1:
        self.__UpdateScore(m.team1, Columns.Victories, 1)
      elif m.matchWinner is MatchWinnerTypes.Team2:
        self.__UpdateScore(m.team2, Columns.Victories, 1)

      self.__UpdateScore(m.team1, Columns.PlayedMatches, 1)
      self.__UpdateScore(m.team2, Columns.PlayedMatches, 1)

      d = Classification.__GetMatchScoreData(m)

      self.__UpdateScore(m.team1, Columns.SetBalance, d.setBalanceT1)
      self.__UpdateScore(m.team1, Columns.GameBalance, d.gameBalanceT1)
      self.__UpdateScore(m.team1, Columns.SetsWon, d.setsT1)
      self.__UpdateScore(m.team1, Columns.GamesWon, d.gamesT1)

      self.__UpdateScore(m.team2, Columns.SetBalance, d.setBalanceT2)
      self.__UpdateScore(m.team2, Columns.GameBalance, d.gameBalanceT2)
      self.__UpdateScore(m.team2, Columns.SetsWon, d.setsT2)
      self.__UpdateScore(m.team2, Columns.GamesWon, d.gamesT2)


  def __UpdateGroups(self, groups:list[list[Team]]) -> None:
    for i, group in enumerate(groups):
      for team in group:
        if team.name in self.classification.index:
          self.classification.at[team.name, Columns.Group.name] = i + 1


  def __GetDirectMatchMatches(self, teamNames:set[str]) -> list[Match]:
    return [
      match for match in self.matches
      if (
        match.team1 is not None
        and match.team2 is not None
        and match.team1.name in teamNames
        and match.team2.name in teamNames
      )
    ]


  def __GetDirectMatchScore(self, tiedTeamNames:list[str], directMatchSortColumns:list[Columns]) -> dict[str, int]:
    directMatches = self.__GetDirectMatchMatches(set(tiedTeamNames))
    if len(directMatches) == 0:
      return {teamName: 0 for teamName in tiedTeamNames}

    directClassification = Classification(directMatches, list(directMatchSortColumns))
    directDf = directClassification.classification

    ordered = OrderDf(directDf, directMatchSortColumns)
    scores = {}
    score = len(tiedTeamNames)
    lastValues = None
    lastScore = score

    for _, (teamName, row) in enumerate(ordered.iterrows()):
      values = tuple(row[col.name] for col in directMatchSortColumns)
      if lastValues is not None and values != lastValues:
        score -= 1
        lastScore = score

      scores[teamName] = lastScore
      lastValues = values

    return {teamName: scores.get(teamName, 0) for teamName in tiedTeamNames}


  def __UpdateDirectMatch(self, sortColumns:list[Columns]) -> None:
    if Columns.DirectMatch not in sortColumns:
      return

    directMatchIndex = sortColumns.index(Columns.DirectMatch)
    previousSortColumns = sortColumns[:directMatchIndex]
    if len(previousSortColumns) == 0:
      return

    directMatchSortColumns = [
      column for column in sortColumns
      if column is not Columns.DirectMatch
    ]

    groupByColumns = [column.name for column in previousSortColumns]
    if self.hasGroups:
      groupByColumns.insert(0, Columns.Group.name)

    for _, tiedDf in self.classification.groupby(groupByColumns, dropna=False):
      if len(tiedDf) <= 1:
        continue

      tiedTeamNames = tiedDf.index.tolist()
      directMatchScores = self.__GetDirectMatchScore(tiedTeamNames, directMatchSortColumns)
      for teamName, score in directMatchScores.items():
        self.classification.at[teamName, Columns.DirectMatch.name] = score


  def __UpdatePositionColumn(self, orderedDf:pd.DataFrame, postionCol:Literal[Columns.GroupPosition, Columns.Position], sortColumns:list[Columns]) -> None:
    currentPosition = 1
    lastValues = None

    for i, (teamName, row) in enumerate(orderedDf.iterrows(), start=1): # this logic makes positions = 1, 1, 3 in case the first two teams are tied.
      values = tuple(row[col.name] for col in sortColumns)

      if lastValues is None:
        currentPosition = 1
      elif values != lastValues:
        currentPosition = i

      self.classification.at[teamName, postionCol.name] = currentPosition
      lastValues = values


  def __UpdateGroupPositions(self, sortColumns:list[Columns]) -> None:
    if not self.hasGroups:
      return

    for _, groupDf in self.classification.groupby(Columns.Group.name):
      ordered = OrderDf(groupDf, sortColumns)
      self.__UpdatePositionColumn(ordered, Columns.GroupPosition, sortColumns)


  def __UpdatePositions(self, sortColumns:list[Columns]) -> None:
    sortColumns.append(Columns.TieDraw)
    self.__UpdateGroupPositions(sortColumns)

    sortColumns = [Columns.GroupPosition, *sortColumns]
    ordered = OrderDf(self.classification, sortColumns)
    self.__UpdatePositionColumn(ordered, Columns.Position, sortColumns)

    self.classification = OrderDf(self.classification)
