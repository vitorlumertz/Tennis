from googleapiclient.discovery import build, Resource
from oauth2client.service_account import ServiceAccountCredentials
from typing import Any
import gspread
from gspread.utils import ValueInputOption
import pandas as pd


class GoogleSheetsConnection:
  def __init__(self, sheetTitle:str, folderId:str):
    self.credentials = self.__GetGoogleCredentials()
    self.service = self.__GetGoogleService()
    self.gspreadClient = self.__GetGspreadClient()
    self.sheet = self.__GetSheet(sheetTitle, folderId)


  def __GetGoogleCredentials(self) -> ServiceAccountCredentials:
    kCredentialFileNAme = 'credential.json'
    kScopes = [
      'https://spreadsheets.google.com/feeds',
      'https://www.googleapis.com/auth/drive',
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
      filename = kCredentialFileNAme,
      scopes = kScopes,
    )

    return creds


  def __GetGoogleService(self) -> Resource:
    return build('sheets', 'v4', credentials=self.credentials)


  def __GetGspreadClient(self) -> gspread.Client:
    return gspread.authorize(self.credentials)


  def __GetSheet(self, sheetTitle:str, folderId:str) -> gspread.Spreadsheet:
    return self.gspreadClient.open(title=sheetTitle, folder_id=folderId)


  def AddWorkSheet(self, workSheetName:str):
    requests = [{
      "addSheet": {
        "properties": {
          "title": workSheetName
        }
      }
    }]

    return self.service.spreadsheets().batchUpdate(
      spreadsheetId = self.sheet.id,
      body = {"requests": requests}
    ).execute()


  def GetWorkSheetData(self, workSheetNumber:int) -> pd.DataFrame:
    worksheet = self.sheet.get_worksheet(workSheetNumber)
    return pd.DataFrame(worksheet.get_all_records())


  def WriteInWorkSheet(self, workSheetName:str, cellsRange:str, values:list[list[Any]], isFormula:bool=False):
    valueInputOption = ValueInputOption.raw.value
    if isFormula:
      valueInputOption = ValueInputOption.user_entered.value

    sheetRange = workSheetName + '!' + cellsRange

    self.service.spreadsheets().values().update(
      spreadsheetId = self.sheet.id,
      range = sheetRange,
      valueInputOption = valueInputOption,
      body = {"values": values}
    ).execute()