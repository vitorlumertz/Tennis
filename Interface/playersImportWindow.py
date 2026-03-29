from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import messagebox


def ImportPlayers(app:"TournamentApp", window:tk.Toplevel, sheetName:str, folderId:str, worksheetNumberStr:str) -> None:
  try:
    worksheetNumber = int(worksheetNumberStr)
  except Exception:
    messagebox.showerror("Erro", "Número da guia deve ser um inteiro.")
    window.destroy()
    return

  try:
    failedImports = app.tournament.ImportPlayersFromGoogleSheet(sheetName, folderId, worksheetNumber)
    if failedImports:
      text = f"{len(failedImports)} importações com erro:\n\n"
      for failedImport in failedImports:
        text += f"{failedImport.Category} - {failedImport.Player}.\n"
      messagebox.showerror("Erro", f"{text}")

  except Exception as e:
    messagebox.showerror("Erro", f"Erro na importação!\n\n{e}.")
    window.destroy()


def OpenImportPlayersWindow(app:"TournamentApp") -> None:
  if app.tournament is None:
    messagebox.showerror("Erro", "Nenhum torneio carregado ou iniciado.")
    return

  if (app.tournament.categories is None) or (len(app.tournament.categories) == 0):
    messagebox.showerror("Erro", "Nenhuma categoria criada no torneio.")
    return

  window = tk.Toplevel(app)
  window.title("Importar Inscritos")
  window.geometry("600x500")

  tk.Label(window, text="Informe os dados da planilha eletrônica do Google Sheets", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome da planilha:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="ID da pasta:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  folderIdEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  folderIdEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Número da guia:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  worksheetNumberEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  worksheetNumberEntry.pack(anchor="w", padx=10)

  tk.Button(
    window,
    text="Importar",
    command=lambda: ImportPlayers(app, window, nameEntry.get(), folderIdEntry.get(), worksheetNumberEntry.get()),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(20,5))
