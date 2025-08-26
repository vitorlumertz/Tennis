from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from matchTeams import Player, Double
from tennisEnums import MatchTypes


def CreateTeam(
  app: "TournamentApp",
  window: tk.Toplevel,
  categoryName: str,
  name1Entry: tk.Entry,
  name2Entry: tk.Entry,
  seedNumberCombo: ttk.Combobox,
  isDoublesPage: bool,
  isUpdate: bool,
  oldTeamName: str,
):
  name1 = name1Entry.get()
  name2 = name2Entry.get() if isDoublesPage else ""
  try:
    seedNumber = int(seedNumberCombo.get())
  except Exception:
    seedNumber = 0

  if isDoublesPage:
    player1 = Player(name1)
    player2 = Player(name2)
    team = Double(player1, player2, seedNumber)
  else:
    team = Player(name1, seedNumber)

  category = app.tournament.GetCategory(categoryName)
  try:
    if isUpdate:
      teams = category.teams
      if (not isDoublesPage) and (category.matchType is MatchTypes.Double):
        teams = category.players
      teams.pop(oldTeamName)
    category.AddTeam(team)
  except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível adicionar {team.name} na categoria {categoryName}.\n\n{e}")
    window.destroy()
    return

  if isUpdate:
    window.destroy()

  app.UpdateTeamsTables(categoryName, isDoublesPage)


def OpenTeamWindow(app:"TournamentApp", categoryName:str, isDoublesPage=False, isUpdate=False, row=None):
  title = "Dupla" if isDoublesPage else "Jogador"
  window = tk.Toplevel(app)
  window.title(title)
  window.geometry("600x500")

  text = "Configure a Dupla" if isDoublesPage else "Configure o Jogador"
  tk.Label(window, text=text, font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome do Jogador:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  name1Entry = tk.Entry(window, width=50, font=('Arial, 12'))
  name1Entry.pack(anchor="w", padx=10)

  name2Entry = tk.Entry(window, width=50, font=('Arial, 12'))
  if isDoublesPage:
    tk.Label(window, text="Nome do Jogador:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
    name2Entry.pack(anchor="w", padx=10)

  tk.Label(window, text="Número de Cabeça de Chave:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  options = [str(i) for i in range(21)]
  default = options[0]
  seedNumberCombo = ttk.Combobox(
    window,
    textvariable=default,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  seedNumberCombo.pack(anchor="w", padx=10)

  if isUpdate:
    if isDoublesPage:
      doubleName = row[0]
      names = doubleName.split(',')
      name1 = names[0]
      name2 = names[1]
      name2Entry.delete(0, tk.END)
      name2Entry.insert(0, name2)
    else:
      name1 = row[0]
    name1Entry.delete(0, tk.END)
    name1Entry.insert(0, name1)
    seedNumber = row[1]
    seedNumberCombo.set(seedNumber)
    oldTeamName = row[0]
  else:
    oldTeamName = ""

  text1 = "Atualizar " if isUpdate else "Adicionar "
  text2 = "Dupla" if isDoublesPage else "Jogador"
  text = text1 + text2
  tk.Button(
    window,
    text=text,
    command=lambda: CreateTeam(app, window, categoryName, name1Entry, name2Entry, seedNumberCombo, isDoublesPage, isUpdate, oldTeamName),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(15,5))