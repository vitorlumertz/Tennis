from gspread.utils import rowcol_to_a1
from .googleSheetsUtils import GoogleSheetsConnection

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournament import Tournament


# Formulas definitions
kIf = "SE"
kSumIf = "SOMASE"
kOrder = "ORDEM"
kCountIfs = "CONT.SES"
kAnd = "E"
kFalse = "FALSO"


def rowcol_to_fixed_a1(row:int, column:int, isFixed:bool=False) -> str:
  a1 = rowcol_to_a1(row, column)
  if isFixed:
    return f"${a1[0]}${a1[1:]}"
  return a1


def GetRange(row1:int, column1:int, row2:int|None=None, column2:int|None=None, isFixed:bool=False) -> str:
  range = rowcol_to_fixed_a1(row1, column1, isFixed)
  if row2 is None:
    return range
  return range + ":" + rowcol_to_fixed_a1(row2, column2, isFixed)


def GetStageName(stage:int) -> str:
  stageName = {
    1: "Final",
    2: "Semifinal",
    4: "Quartas de Final",
    8: "Oitavas de Final",
    16: "R32",
  }.get(stage)

  if stageName is None:
    raise Exception(f"Não foi possível obter a fase eliminatória para o valor {stage}.")

  return stageName


def ExportGroupStage(tournament:"Tournament", gsConnection:GoogleSheetsConnection) -> None:

  # Columns definitions
  kCategoryName = 1
  kGroupName = 1
  kPosition = 1
  kTeam = 2
  kVictories = 3
  kMatches = 4
  kGamesScore = 5
  kGroupMatchesTitle = 7
  kCourt = 7
  kTeam1 = 8
  kTeam2 = 10
  kGamesT1 = 11
  kGamesT2 = 12
  kVictoryT1 = 13
  kVictoryT2 = 14
  kGamesScoreT1 = 15
  kGamesScoreT2 = 16


  def AddCategoryWorkSheet():
    nonlocal classificationValues
    gsConnection.AddWorkSheet(workSheetName)
    classificationValues.append(["Categoria " + category.name])
    classificationValues.append([])


  def AddGroupName():
    nonlocal classificationValues
    groupName = "Grupo " + str(i+1)
    classificationValues.append([groupName])


  def AddGroupHead():
    nonlocal classificationValues
    classificationValues.append(groupHead)


  def AddGroupClassification():
    nonlocal classificationValues
    headRow = len(classificationValues)
    groupLastRow = headRow + len(group)
    groupMatchesLastRow = headRow + len(groupMatches)
    firstTeamRow = headRow + 1

    team1Range = GetRange(firstTeamRow, kTeam1, groupMatchesLastRow, kTeam1, isFixed=True)
    team2Range = GetRange(firstTeamRow, kTeam2, groupMatchesLastRow, kTeam2, isFixed=True)
    victoryT1Range = GetRange(firstTeamRow, kVictoryT1, groupMatchesLastRow, kVictoryT1, isFixed=True)
    victoryT2Range = GetRange(firstTeamRow, kVictoryT2, groupMatchesLastRow, kVictoryT2, isFixed=True)
    victoriesRange = GetRange(firstTeamRow, kVictories, groupLastRow, kVictories, isFixed=True)
    gamesScoreT1Range = GetRange(firstTeamRow, kGamesScoreT1, groupMatchesLastRow, kGamesScoreT1, isFixed=True)
    gamesScoreT2Range = GetRange(firstTeamRow, kGamesScoreT2, groupMatchesLastRow, kGamesScoreT2, isFixed=True)
    gamesScoreRange = GetRange(firstTeamRow, kGamesScore, groupLastRow, kGamesScore, isFixed=True)

    for team in group:
      row = len(classificationValues) + 1
      teamCell = GetRange(row, kTeam)
      victoriesCell = GetRange(row, kVictories)
      gamesScoreCell = GetRange(row, kGamesScore)

      positionFormula = f'={kOrder}({victoriesCell};{victoriesRange};{kFalse}) + {kCountIfs}({victoriesRange};{victoriesCell};{gamesScoreRange};">" & {gamesScoreCell})'
      victoriesFormula = f'={kSumIf}({team1Range};{teamCell};{victoryT1Range}) + {kSumIf}({team2Range};{teamCell};{victoryT2Range})'
      matchesFormula = f'={kCountIfs}({team1Range};{teamCell};{gamesScoreT1Range};"<>0") + {kCountIfs}({team2Range};{teamCell};{gamesScoreT2Range};"<>0")'
      gamesScoreFormula = f'={kSumIf}({team1Range};{teamCell};{gamesScoreT1Range}) + {kSumIf}({team2Range};{teamCell};{gamesScoreT2Range})'

      classificationValues.append([positionFormula, team.name, victoriesFormula, matchesFormula, gamesScoreFormula])

    emptyRows = len(groupMatches) - len(group) + 1
    for _ in range(emptyRows):
      classificationValues.append([])


  def AddGroupMatchesName():
    nonlocal matchesValues
    groupMatchesStr = "Jogos do Grupo " + str(i+1)
    matchesValues.append([groupMatchesStr])


  def AddGroupMatchesHead():
    nonlocal matchesValues
    matchesValues.append(matchesHead)


  def AddGroupMatches():
    nonlocal matchesValues
    for match in groupMatches:
      row = len(matchesValues) + 3
      gamesT1Cell = GetRange(row, kGamesT1)
      gamesT2Cell = GetRange(row, kGamesT2)
      victoryT1Formula = f'={kIf}({gamesT1Cell}>{gamesT2Cell};1;0)'
      victoryT2Formula = f'={kIf}({gamesT2Cell}>{gamesT1Cell};1;0)'
      gamesScoreT1Formula = f'={gamesT1Cell}-{gamesT2Cell}'
      gamesScoreT2Formula = f'={gamesT2Cell}-{gamesT1Cell}'

      matchesValues.append(["", match.team1.name, "x", match.team2.name, '', '', victoryT1Formula, victoryT2Formula, gamesScoreT1Formula, gamesScoreT2Formula])

    matchesValues.append([])


  groupHead = ["Posição", "Dupla", "Vitórias", "Partidas Jogadas", "Saldo de Games"]
  matchesHead = ["Quadra", "Dupla 1", "", "Dupla 2", "Games Dupla 1", "Games Dupla 2", "Vitória D1", "Vitória D2", "SG D1", "SG D2"]

  for category in tournament.categories.values():
    if (category.groups is None) or (len(category.groups) == 0):
      continue

    workSheetName = "Grupos " + category.name
    classificationValues = []
    matchesValues = []
    AddCategoryWorkSheet()

    for i, group in enumerate(category.groups):
      groupMatches = category.GetGroupMatches(i)
      AddGroupName()
      AddGroupHead()
      AddGroupClassification()
      AddGroupMatchesName()
      AddGroupMatchesHead()
      AddGroupMatches()

    gsConnection.WriteInWorkSheet(workSheetName, GetRange(1, kPosition, len(classificationValues), kGamesScore), classificationValues, isFormula=True)
    gsConnection.WriteInWorkSheet(workSheetName, GetRange(3, kCourt, len(matchesValues)+2, kGamesScoreT2), matchesValues, isFormula=True)


def ExportEliminatoryStage(tournament:"Tournament", gsConnection:GoogleSheetsConnection, categoriesStages:dict[str,int]) -> None:

  # Columns definitions
  kCategoryName = 1
  kCourt = 1
  kStage = 2
  kTeam1 = 3
  kTeam2 = 5
  kGamesT1 = 6
  kGamesT2 = 7


  def GetWinnerFormula(fatherStageRow:int) -> str:
    team1Cell = GetRange(fatherStageRow, kTeam1)
    team2Cell = GetRange(fatherStageRow, kTeam2)
    gamesT1Cell = GetRange(fatherStageRow, kGamesT1)
    gamesT2Cell = GetRange(fatherStageRow, kGamesT2)
    return f'={kIf}({kAnd}({gamesT1Cell}="";{gamesT2Cell}="");"";{kIf}({gamesT1Cell}>{gamesT2Cell};{team1Cell};{team2Cell}))'


  def AddMatches():
    nonlocal values
    fatherStageRow = len(values) + 1
    categoryStage = categoriesStages[category.name]
    stage = categoryStage
    while stage >= 1:
      stageName = GetStageName(stage)
      stageCount = 0
      while stageCount < stage:
        if stage == categoryStage:
          team1 = ""
          team2 = ""
        else:
          team1 = GetWinnerFormula(fatherStageRow)
          fatherStageRow += 1
          team2 = GetWinnerFormula(fatherStageRow)
          fatherStageRow += 1
        values.append(["", stageName, team1, "x", team2])
        stageCount += 1
      stage /= 2


  workSheetName = "Fase Eliminatória"
  gsConnection.AddWorkSheet(workSheetName)
  head = ["Quadra", "Fase", "Dupla 1", "", "Dupla 2", "Games D1", "Games D2"]
  values = []

  for category in tournament.categories.values():
    if not category.hasEliminationPhase:
      continue
    if category.name not in categoriesStages:
      raise Exception(f"A categoria '{category.name}' tem fase eliminatória, mas nenhuma fase inicial foi informada para ela na exportação.")
    categoryName = "Categoria " + category.name
    values.append([categoryName])
    values.append(head)
    AddMatches()
    for _ in range(2):
      values.append([])

  gsConnection.WriteInWorkSheet(workSheetName, GetRange(1, kCourt, len(values), kGamesT2), values, isFormula=True)


def ExportTournamentToGoogleSheets(tournament:"Tournament", sheetTitle:str, folderId:str, categoriesStages:dict[str,int]) -> None:
  gsConnection = GoogleSheetsConnection(sheetTitle, folderId)
  ExportGroupStage(tournament, gsConnection)
  ExportEliminatoryStage(tournament, gsConnection, categoriesStages)