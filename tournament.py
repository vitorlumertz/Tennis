from typing import Literal

from classification import Columns, DEFAULT_CLASSIFICATION_CRITERIA, GetDefaultResultPoints, ResultPoints
from tennisEnums import *
from tennisExceptions import *
from category import Category
from matchTeams import Team, Player
from GoogleSheets.playersImport import GetPlayersFromSheet
from GoogleSheets.tournamentExport import ExportTournamentToGoogleSheets


class Tournament:
  def __init__(
    self,
    name: str,
    sets: Literal[1,3,5] = 3,
    setType: SetTypes = SetTypes.NormalSet,
    lastSetType: SetTypes = SetTypes.MatchTieBreak,
    categories: dict[str, Category] | None = None,
    oldDoubles: list[tuple[str, str]] | None = None,
    classificationCriteria: list[Columns] | None = None,
    resultPoints: ResultPoints | None = None,
  ):
    if sets not in [1, 3, 5]:
      raise ValueError(f"Sets must be 1, 3 or 5. {sets} was given.")

    self.name = name
    self.sets = sets
    self.setType = setType
    self.lastSetType = lastSetType
    self.categories = {} if categories is None else categories
    self.oldDoubles = [] if oldDoubles is None else oldDoubles
    self.classificationCriteria = (classificationCriteria if classificationCriteria is not None else DEFAULT_CLASSIFICATION_CRITERIA).copy()
    self.resultPoints = resultPoints.copy() if resultPoints is not None else GetDefaultResultPoints(sets)


  def __repr__(self):
    return (
      f"Name: {self.name}\n"
      f"Number of Sets: {self.sets}\n"
      f"Set Type: {self.setType.name}\n"
      f"Last Set Type: {self.lastSetType.name}\n"
      f"Number of Categories: {len(self.categories)}\n"
      f"Number of Old Dobles: {len(self.oldDoubles)}\n"
    )


  def AddCategory(self, category:Category):
    if (category.name not in self.categories):
      self.categories[category.name] = category
    else:
      raise DuplicatedCategory(category.name)


  def GetCategory(self, categoryName:str) -> Category:
    if categoryName not in self.categories:
      raise CategoryNotFound(categoryName)

    return self.categories[categoryName]


  def AddTeam(self, team:Team, categoryName:str):
    category = self.GetCategory(categoryName)
    category.AddTeam(team)


  def AddOldDouble(self, player1Name:str, player2Name:str):
    self.oldDoubles.append((player1Name, player2Name))


  def ImportPlayersFromGoogleSheet(self, sheetTitle:str, folderId:str, worksheetNumber:int):
    data = GetPlayersFromSheet(sheetTitle, folderId, worksheetNumber)
    failedRows = []
    for row in data.itertuples():
      player = Player(row.Player)
      try:
        self.AddTeam(player, row.Category)
      except Exception:
        failedRows.append(row)

    return failedRows


  def ExportToGoogleSheets(self, sheetTitle:str, folderId:str, categoriesStages:dict[str,int]) -> None:
    ExportTournamentToGoogleSheets(self, sheetTitle, folderId, categoriesStages)


  def StartCategory(self, categoryName):
    category = self.GetCategory(categoryName)
    if not category.isInitialized:
      if category.isRandomDoubles:
        category.DrawDubles(self.oldDoubles)
      category.GetFirstRound(self.sets, self.setType, self.lastSetType)
      category.GetBracket()
      category.CompleteMatches(self.sets, self.setType, self.lastSetType)
      category.SortMatches()
      category.isInitialized = True


  def StartCategories(self):
    for categoryName in self.categories.keys():
      self.StartCategory(categoryName)


  def UpdateBrackets(self):
    for category in self.categories.values():
      category.UpdateBracket(self.classificationCriteria, self.resultPoints)
