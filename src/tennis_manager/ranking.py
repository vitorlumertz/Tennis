from enum import Enum
import pandas as pd

from tennis_manager.category import Category
from tennis_manager.classification import Columns as ClassificationColumns
from tennis_manager.tennisEnums import MatchTypes, MatchWinnerTypes, CategoryTypes
from tennis_manager.tournament import Tournament


class RankingColumns(Enum):
  Category = 1
  Position = 2
  Name = 3
  Points = 4
  DiscardedValue = 5


class Ranking:
  def __init__(
    self,
    name: str,
    tournaments: list[Tournament] | None = None,
    defaultEliminatoryPoints: dict[int, int] | None = None,
    defaultRoundRobinPoints: dict[int, int] | None = None,
    isIndividual: bool = True,
    discardWorstValue: bool = True,
  ):
    self.name = name

    self.defaultEliminatoryPoints = defaultEliminatoryPoints or {
      0: 10, # 0 = champion
      1: 8,  # 1 = finalist
      2: 6,  # 2 = semifinalist ...
      4: 4,
      8: 3,
      16: 2,
      32: 1,
    }

    self.defaultRoundRobinPoints = defaultRoundRobinPoints or {
      1: 10, # keys mean position
      2: 8,
      3: 6,
      4: 4,
    }

    self.isIndividual = isIndividual
    self.discardWorstValue = discardWorstValue

    columns = [
      RankingColumns.Category.name,
      RankingColumns.Position.name,
      RankingColumns.Name.name,
      RankingColumns.Points.name,
      RankingColumns.DiscardedValue.name,
    ]
    self.data = pd.DataFrame(columns=columns)

    self.tournaments = {}
    for t in tournaments:
      self.AddTournament(t)


  def __GetCategoryPoints(self, category:Category) -> dict[str, int]:

    def AddTeamPoints(teamsPoints:dict[str,int], teamName:str, points:int) -> None:
      if (category.matchType is MatchTypes.Double) and (self.isIndividual):
        for playerName in teamName.split('/'):
          teamsPoints[playerName] = points
      else:
        teamsPoints[teamName] = points


    def GetEliminatoryPoints(stage:int) -> int:
      try:
        return self.defaultEliminatoryPoints[stage]
      except KeyError:
        raise Exception(f"Stage {stage} is not defined in eliminatory points.")


    teamsPoints = {}
    if category.groups is not None:
      for i, group in enumerate(category.groups):
        classification = category.GetClassification(i)
        last = classification.GetTeamNameByPosition(len(group))
        for teamName, teamData in classification.classification.iterrows():
          victories = int(teamData[ClassificationColumns.Victories.name])
          position = int(teamData[ClassificationColumns.GroupPosition.name])

          if (
            category.categoryType is CategoryTypes.RoundRobin
            and position in self.defaultRoundRobinPoints
            and teamName != last
          ):
            points = self.defaultRoundRobinPoints[position]
          else:
            points = victories + 1

          AddTeamPoints(teamsPoints, teamName, points)

    category.SortMatches()
    for match in category.matches.values():
      if not match.matchKey.IsSingleElimination():
        continue

      stage = match.matchKey.firstInfo
      points = GetEliminatoryPoints(stage)

      if match.team1 is not None:
        AddTeamPoints(teamsPoints, match.team1.name, points)

      if match.team2 is not None:
        AddTeamPoints(teamsPoints, match.team2.name, points)

      if stage == 1:
        champion = None
        if match.matchWinner == MatchWinnerTypes.Team1:
          champion = match.team1
        elif match.matchWinner == MatchWinnerTypes.Team2:
          champion = match.team2

        if champion:
          championPoints = GetEliminatoryPoints(0)
          AddTeamPoints(teamsPoints, champion.name, championPoints)

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


  def __GetStagePointValues(self) -> list[int]:
    stageColumns = self.__GetStageColumns()
    values = []
    for col in stageColumns:
      values.extend(self.data[col].dropna().tolist())

    return sorted(set(values), reverse=True)


  def __UpdateDiscardedValues(self) -> None:
    if not self.discardWorstValue:
      self.data[RankingColumns.DiscardedValue.name] = 0
      return

    stageColumns = self.__GetStageColumns()
    minimumValues = self.data[stageColumns].min(axis=1, skipna=False)
    self.data[RankingColumns.DiscardedValue.name] = minimumValues.fillna(0)


  def __UpdatePoints(self) -> None:
    stageColumns = self.__GetStageColumns()
    points = self.data[stageColumns].sum(axis=1) - self.data[RankingColumns.DiscardedValue.name]
    self.data[RankingColumns.Points.name] = points


  def __UpdatePositions(self) -> None:
    stageColumns = self.__GetStageColumns()
    stagePointValues = self.__GetStagePointValues()
    tieBreakerColumns = [f"__TieBreaker_{value}" for value in stagePointValues]

    for _, categoryDf in self.data.groupby(RankingColumns.Category.name):
      categoryDf = categoryDf.copy()
      for pointValue, tieBreakerColumn in zip(stagePointValues, tieBreakerColumns):
        categoryDf[tieBreakerColumn] = categoryDf[stageColumns].eq(pointValue).sum(axis=1)

      ordered = categoryDf.sort_values(
        by=[RankingColumns.Points.name, *tieBreakerColumns],
        ascending=[False, *[False for _ in tieBreakerColumns]],
      )

      currentPosition = 1
      lastCriteria = None
      for i, (index, row) in enumerate(ordered.iterrows(), start=1):
        criteria = tuple(row[[RankingColumns.Points.name, *tieBreakerColumns]])
        if lastCriteria is None:
          currentPosition = 1
        elif criteria != lastCriteria:
          currentPosition = i

        self.data.at[index, RankingColumns.Position.name] = currentPosition
        lastCriteria = criteria

    self.data = self.data.sort_values(
      by=[
        RankingColumns.Category.name,
        RankingColumns.Position.name,
        RankingColumns.Name.name,
      ],
    ).reset_index(drop=True)


  def AddTournament(self, tournament:Tournament) -> None:
    if tournament.name in self.tournaments:
      raise ValueError(f"Tournament {tournament.name} has already been added to this ranking.")

    self.tournaments[tournament.name] = tournament
    rankingStage = len(self.tournaments)
    self.data.insert(rankingStage + 3, str(rankingStage), 0)
    for category in tournament.categories.values():
      for teamName, points in self.__GetCategoryPoints(category).items():
        self.__Upsert(category.name, teamName, rankingStage, points)

    self.__UpdateDiscardedValues()
    self.__UpdatePoints()
    self.__UpdatePositions()


if __name__ == '__main__':
  from tennis_manager.fileReader import ReadInputFile
  tournaments = [
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\1aEtapa\RankingDeDuplas2026_1aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\2aEtapa\RD_2026_2aEtapa_4.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\3aEtapa\RD3aEtapa_8.txt"),
  ]
  ranking = Ranking('RankingTest', tournaments, discardWorstValue=False)
