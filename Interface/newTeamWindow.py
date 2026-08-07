from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tennis_manager.category import Category
from tennis_manager.matchTeams import Player, Double
from tennis_manager.tennisEnums import MatchTypes
from tennis_manager.matchTeams import NormalizeTeamName


def GetAvailableDoublePlayers(category:Category, doubleBeingUpdate:str="") -> dict[str,Player]:
  """Return the players that can be shown in the double selectors.

  When editing an existing double, ``doubleBeingUpdate`` contains its current
  name. That double is ignored so its players remain selectable, while players
  assigned to every other double are removed from the GUI options.
  """
  availablePlayers = dict(category.players)
  for doubleName, double in category.teams.items():
    if doubleName == doubleBeingUpdate:
      continue
    if isinstance(double, Double):
      availablePlayers.pop(double.player1.name, None)
      availablePlayers.pop(double.player2.name, None)
  return availablePlayers


def GetPossibleDoublePartners(category:Category, playerName:str, doubleBeingUpdate:str="") -> list[Player]:
  """Return selector options that obey the random-doubles seed sum rule.

  ``doubleBeingUpdate`` identifies the double currently being edited. It is
  passed to ``GetAvailableDoublePlayers`` so that double's players remain GUI
  options without exposing players assigned to other existing doubles.
  """
  availablePlayers = GetAvailableDoublePlayers(category, doubleBeingUpdate)
  playerName = NormalizeTeamName(playerName)
  player = availablePlayers.pop(playerName, None)
  if player is None or len(availablePlayers) == 0:
    return []

  requiredPartnerSeed = category.GetSeedSumForDrawnDoubles() - player.seedNumber
  return [
    availablePlayer
    for availablePlayer in availablePlayers.values()
    if availablePlayer.seedNumber == requiredPartnerSeed
  ]


def CreateTeam(
  app: "TournamentApp",
  frame: tk.Frame,
  summaryFrame:tk.Frame,
  window: tk.Toplevel,
  categoryName: str,
  name1Entry: tk.Entry,
  name2Entry: tk.Entry,
  seedNumberCombo: ttk.Combobox,
  isDoublesPage: bool,
  isUpdate: bool,
  oldTeamName: str,
  usePlayerSelectors: bool = False,
):
  name1 = name1Entry.get()
  name2 = name2Entry.get() if isDoublesPage else ""
  try:
    seedNumber = int(seedNumberCombo.get())
  except Exception:
    seedNumber = 0

  category = app.tournament.GetCategory(categoryName)
  if isDoublesPage:
    if usePlayerSelectors:
      player1 = category.GetPlayer(name1)
      player2 = category.GetPlayer(name2)
      if player1 is None or player2 is None:
        messagebox.showerror("Erro", "Selecione os dois jogadores da dupla.")
        return
    else:
      player1 = Player(name1)
      player2 = Player(name2)
    team = Double(player1, player2, seedNumber)
  else:
    team = Player(name1, seedNumber)

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

  app.UpdateTeamsContent(frame, summaryFrame, categoryName, isDoublesPage)


def OpenTeamWindow(app:"TournamentApp", frame:tk.Frame, summaryFrame:tk.Frame, categoryName:str, isDoublesPage=False, isUpdate=False, row=None):
  category = app.tournament.GetCategory(categoryName)
  usePlayerSelectors = isDoublesPage and category.isRandomDoubles
  title = "Dupla" if isDoublesPage else "Jogador"
  window = tk.Toplevel(app)
  window.title(title)
  window.geometry("600x500")

  text = "Configure a Dupla" if isDoublesPage else "Configure o Jogador"
  tk.Label(window, text=text, font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome do Jogador:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=5)
  if usePlayerSelectors:
    availablePlayers = GetAvailableDoublePlayers(category, row[0] if isUpdate else "")
    playerNames = list(availablePlayers)
    name1Entry = ttk.Combobox(window, values=playerNames, state="readonly", width=47, font=('Arial', 12))
  else:
    name1Entry = tk.Entry(window, width=50, font=('Arial', 12))
  name1Entry.pack(anchor="w", padx=10)

  if usePlayerSelectors:
    name2Entry = ttk.Combobox(window, values=playerNames, state="readonly", width=47, font=('Arial', 12))
  else:
    name2Entry = tk.Entry(window, width=50, font=('Arial', 12))
  if isDoublesPage:
    tk.Label(window, text="Nome do Jogador:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=5)
    name2Entry.pack(anchor="w", padx=10)

  if usePlayerSelectors:
    doubleBeingUpdate = row[0] if isUpdate else ""

    def UpdatePartnerOptions(selectedCombo, partnerCombo):
      possibleNames = [
        player.name
        for player in GetPossibleDoublePartners(category, selectedCombo.get(), doubleBeingUpdate)
      ]
      partnerCombo["values"] = possibleNames
      if partnerCombo.get() not in possibleNames:
        partnerCombo.set("")

    name1Entry.bind(
      "<<ComboboxSelected>>",
      lambda _event: UpdatePartnerOptions(name1Entry, name2Entry),
    )
    name2Entry.bind(
      "<<ComboboxSelected>>",
      lambda _event: UpdatePartnerOptions(name2Entry, name1Entry),
    )

  tk.Label(window, text="Número de Cabeça de Chave:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=5)
  options = [str(i) for i in range(21)]
  default = options[0]
  seedNumberCombo = ttk.Combobox(
    window,
    textvariable=default,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  seedNumberCombo.pack(anchor="w", padx=10)

  if isUpdate:
    if isDoublesPage:
      doubleName = row[0]
      names = doubleName.split('/')
      name1 = names[0]
      name2 = names[1]
      if usePlayerSelectors:
        name2Entry.set(name2)
      else:
        name2Entry.delete(0, tk.END)
        name2Entry.insert(0, name2)
    else:
      name1 = row[0]
    if usePlayerSelectors:
      name1Entry.set(name1)
    else:
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
    command=lambda: CreateTeam(app, frame, summaryFrame, window, categoryName, name1Entry, name2Entry, seedNumberCombo, isDoublesPage, isUpdate, oldTeamName, usePlayerSelectors),
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(15,5))
