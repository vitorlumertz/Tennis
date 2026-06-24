import pandas as pd
from enum import Enum
from .googleSheetsUtils import GoogleSheetsConnection

from tennis_manager.tournament import Tournament
from tennis_manager.matchTeams import Player


class Columns(Enum):
  Category = 'Category'
  Player = 'Player'


# Folder ID can be found in the folder link. Example: https://drive.google.com/drive/folders/someId -> someId is the folder ID.

def GetPlayersFromSheet(sheetTitle:str, folderId:str, worksheetNumber:int) -> pd.DataFrame:
  googleSheetsConnection = GoogleSheetsConnection(sheetTitle, folderId)

  data = googleSheetsConnection.GetWorkSheetData(worksheetNumber)

  return data[data[Columns.Player.value].fillna("").str.strip().ne("")]


def ImportPlayersFromGoogleSheet(tournament:Tournament, sheetTitle:str, folderId:str, worksheetNumber:int):
  data = GetPlayersFromSheet(sheetTitle, folderId, worksheetNumber)
  failedRows = []
  for row in data.itertuples():
    player = Player(row.Player)
    try:
      tournament.AddTeam(player, row.Category)
    except Exception:
      failedRows.append(row)

  return failedRows
