import pandas as pd
from enum import Enum
from .googleSheetsUtils import GoogleSheetsConnection


class Columns(Enum):
  Category = 'Category'
  Player = 'Player'


# Folder ID can be found in the folder link. Example: https://drive.google.com/drive/folders/someId -> someId is the folder ID.

def GetPlayersFromSheet(sheetTitle:str, folderId:str, worksheetNumber:int) -> pd.DataFrame:
  googleSheetsConnection = GoogleSheetsConnection(sheetTitle, folderId)

  data = googleSheetsConnection.GetWorkSheetData(worksheetNumber)

  return data[data[Columns.Player.value].fillna("").str.strip().ne("")]
