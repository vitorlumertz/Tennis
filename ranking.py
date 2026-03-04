from dataclasses import dataclass
from enum import Enum
import pandas as pd

from tournament import Tournament
from category import Category
from tennisEnums import MatchTypes, MatchWinnerTypes, CategoryTypes


class RankingColumns(Enum):
  Category = 1
  Position = 2
  Name = 3
  Points = 4
  DiscardedValue = 5


@dataclass
class RankingConfig:
  first: int = 10
  second: int = 8
  third: int = 6
  fourth: int = 4
  semifinalist: int = 6
  round8: int = 4
  round16: int = 3
  round32: int = 2
  round64: int = 1
  minimum: int = 1
  isIndividual: bool = True


  def GetStagePoints(self, stage:int) -> int:
    return {
      1: self.second,
      2: self.semifinalist,
      4: self.round8,
      8: self.round16,
      16: self.round32,
      32: self.round64,
    }.get(stage)


  def GetRoundRobinPoints(self, i:int, victories:int) -> int:
    return {
      1: self.first,
      2: self.second,
      3: self.third,
      4: self.fourth,
    }.get(i, self.minimum + victories)


class Ranking:
  def __init__(self, name:str, data:pd.DataFrame, config:RankingConfig):
    self.name = name
    self.data = data
    self.config = config


  def __GetCategoryPoints(self, category:Category) -> dict[str, int]:

    def AddTeamPoints(teamsPoints:dict[str,int], teamName:str, points:int) -> None:
      if (category.matchType is MatchTypes.Double) and (self.config.isIndividual):
        for playerName in teamName.split('/'):
          teamsPoints[playerName] = points
      else:
        teamsPoints[teamName] = points

    teamsPoints = {}
    if category.groups is not None:
      for i in range(len(category.groups)):
        classification, _ = category.GetGroupClassification(i)
        position = 1
        for teamName, teamData in classification.items():
          victories = teamData['Victories']
          if category.categoryType is CategoryTypes.RoundRobin:
            points = self.config.GetRoundRobinPoints(position, victories)
            position += 1
          else:
            points = victories + self.config.minimum
          AddTeamPoints(teamsPoints, teamName, points)
        else:
          if category.categoryType is CategoryTypes.RoundRobin:
            points = self.config.minimum + victories
            AddTeamPoints(teamsPoints, teamName, points)

    for matchKey, match in category.GetEliminatoryMAtches().items():
      stage = int(matchKey[:3])
      points = self.config.GetStagePoints(stage)
      if not match.IsTeamsSet():
        continue
      if match.matchWinner is MatchWinnerTypes.kNone:
        AddTeamPoints(teamsPoints, match.team1.name, points)
        AddTeamPoints(teamsPoints, match.team2.name, points)
      elif match.matchWinner is MatchWinnerTypes.Team1:
        AddTeamPoints(teamsPoints, match.team2.name, points)
        if stage == 1:
          AddTeamPoints(teamsPoints, match.team1.name, self.config.first)
      elif match.matchWinner is MatchWinnerTypes.Team2:
        AddTeamPoints(teamsPoints, match.team1.name, points)
        if stage == 1:
          AddTeamPoints(teamsPoints, match.team2.name, self.config.first)

    return teamsPoints


  def __Upsert(self, categoryName:str, teamName:str, rankingStage:int, points:int) -> None:
    mask = (
      (self.data[RankingColumns.Category.name] == categoryName) &
      (self.data[RankingColumns.Name.name] == teamName)
    )
    if mask.any():
      self.data.loc[mask, str(rankingStage)] = points
    else:
      self.data.loc[len(self.data)] = {
        RankingColumns.Category.name: categoryName,
        RankingColumns.Name.name: teamName,
        str(rankingStage): points,
      }


  def __GetStageColumns(self) -> list[str]:
    return [col for col in self.data.columns if col.isdigit()]


  def __UpdateDiscardedValues(self) -> None:
    stageColumns = self.__GetStageColumns()
    minimumValues = self.data[stageColumns].min(axis=1, skipna=False)
    self.data[RankingColumns.DiscardedValue.name] = minimumValues.fillna(0)


  def __UpdatePoints(self) -> None:
    stageColumns = self.__GetStageColumns()
    points = self.data[stageColumns].sum(axis=1) - self.data[RankingColumns.DiscardedValue.name]
    self.data[RankingColumns.Points.name] = points


  def AddRankingStage(self, rankingStage:int) -> None:
    if str(rankingStage) not in self.data.columns:
      cols = list(self.data.columns)
      if str(rankingStage-1) in cols:
        i = cols.index(str(rankingStage-1)) + 1
      else:
        i = len(cols)
      self.data.insert(i, str(rankingStage), 0)


  def AddTournament(self, tournament:Tournament, rankingStage:int) -> None:
    self.AddRankingStage(rankingStage)
    for category in tournament.categories.values():
      for teamName, points in self.__GetCategoryPoints(category).items():
        self.__Upsert(category.name, teamName, rankingStage, points)

    self.__UpdateDiscardedValues()
    self.__UpdatePoints()


def GetRankingData(filePath:str) -> pd.DataFrame:
  return pd.read_csv(filePath)


if __name__ == '__main__':
  from fileReader import ReadInputFile
  filePath = '.\\TestData\\RankingExample1.csv'
  data = GetRankingData(filePath)
  ranking = Ranking('RankingTest', data, RankingConfig())
  tournament = ReadInputFile('.\\TestData\\TournamentDoublesExample5.txt')
  ranking.AddTournament(tournament, 4)
  print()