import pandas as pd
import gspread
from enum import Enum
from oauth2client.service_account import ServiceAccountCredentials


class Columns(Enum):
  Category = 'Category'
  Player = 'Player'


# Folder ID can be found in the folder link. Example: https://drive.google.com/drive/folders/someId -> someId is the folder ID.

def GetPlayersFromSheet(sheetTitle:str, folderId:str, worksheetNumber:int) -> pd.DataFrame:
  kCredentialFileNAme = 'credential.json'
  kScopes = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
  ]
  creds = ServiceAccountCredentials.from_json_keyfile_name(
    filename = kCredentialFileNAme,
    scopes = kScopes,
  )

  client = gspread.authorize(creds)

  sheet = client.open(title=sheetTitle, folder_id=folderId)
  worksheet = sheet.get_worksheet(worksheetNumber)

  data = pd.DataFrame(worksheet.get_all_records())
  return data[data[Columns.Player.value].fillna("").str.strip().ne("")]
