from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import messagebox


def Export(app:"TournamentApp", window:tk.Toplevel, sheetName:str, folderId:str, categoriesStagesStr:str) -> None:
  try:
    categoriesStages = {}
    categoriesStagesList = categoriesStagesStr.split(';')
    for categoryStageStr in categoriesStagesList:
      categoryStageList = categoryStageStr.split(':')
      categoryName = categoryStageList[0]
      categoryStage = int(categoryStageList[1])
      categoriesStages[categoryName] = categoryStage

  except Exception as e:
    messagebox.showerror("Erro", f"Erro no parse das fases iniciais na chave eliminatória por categoria: \n\n{e}.")
    window.destroy()
    return

  try:
    app.tournament.ExportToGoogleSheets(sheetName, folderId, categoriesStages)
  except Exception as e:
    messagebox.showerror("Erro", f"Erro na exportação!\n\n{e}.")
    window.destroy()


def OpenExportTournamentWindow(app:"TournamentApp") -> None:
  if app.tournament is None:
    messagebox.showerror("Erro", "Nenhum torneio carregado ou iniciado.")
    return

  if (app.tournament.categories is None) or (len(app.tournament.categories) == 0):
    messagebox.showerror("Erro", "Nenhuma categoria criada no torneio.")
    return

  window = tk.Toplevel(app)
  window.title("Exportar Torneio")
  window.geometry("1000x500")

  tk.Label(window, text="Informe os dados da planilha eletrônica do Google Sheets", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome da planilha:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="ID da pasta:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  folderIdEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  folderIdEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Fase inicial na chave eliminatória por categoria:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  categoriesStagesStr = tk.Entry(window, width=50, font=('Arial, 12'))
  categoriesStagesStr.pack(anchor="w", padx=10)

  tk.Button(
    window,
    text="Exportar",
    command=lambda: Export(app, window, nameEntry.get(), folderIdEntry.get(), categoriesStagesStr.get()),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(20,5))
