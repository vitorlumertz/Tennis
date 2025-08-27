from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tennisEnums import ScoreTypes
from category import Category
from match import Match
from fileReader import GetScore


def UpdateScore(app:"TournamentApp", window:tk.Toplevel, category:Category, match:Match, scoreStr:str, scoreType:ScoreTypes):
  window.destroy()
  score = GetScore(scoreStr)
  match.SetScore(score, scoreType)
  app.tournament.UpdateBrackets()
  app.UpdateMatchesContent(category.name)


def OpenScoreWindow(app:"TournamentApp", category:Category, match:Match):
  window = tk.Toplevel(app)
  window.title("Resultado de Jogo")
  window.geometry("600x300")

  team1Name = ""
  if match.team1 is not None:
    team1Name = match.team1.name
  team2Name = ""
  if match.team2 is not None:
    team2Name = match.team2.name
  tk.Label(window, text=f"{team1Name} x {team2Name}", font=('Arial, 14')).pack(anchor="w", padx=10, pady=5)

  tk.Label(window, text="Placar:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  scoreEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  scoreEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = [
    ScoreTypes.Normal.name,
    ScoreTypes.WO_to_T1.name,
    ScoreTypes.WO_to_T2.name,
    ScoreTypes.DoubleWO.name,
    ScoreTypes.T1Forfeit.name,
    ScoreTypes.T2Forfeit.name,
    ScoreTypes.NotDefined.name,
  ]
  scoreType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=scoreType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Button(
    window,
    text="Atualizar",
    command=lambda: UpdateScore(app, window, category, match, scoreEntry.get(), ScoreTypes[scoreType.get()]),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(20,5))


def CreateMatchesTable(app:"TournamentApp", category:Category, matches:dict[str, Match], teamStr:str, labelTitle:str=''):
  frame = tk.Frame(app.contentFrame, bg="white")
  frame.pack(anchor="w", padx=10, pady=10)
  if labelTitle != '':
    tk.Label(frame, text=labelTitle, font=("Arial", 12), bg="white").pack(pady=(0,2), anchor="w")
  table = ttk.Treeview(frame, columns=('team1', 'team2', 'score', 'key'), show="headings", height=len(matches))
  table.heading('team1', text=f"{teamStr} 1")
  table.heading('team2', text=f"{teamStr} 2")
  table.heading('score', text="Placar")
  table.heading('key', text="key")
  table.column('team1', width=250, anchor="center")
  table.column('team2', width=250, anchor="center")
  table.column('score', width=150, anchor="center")
  table.column('key', width=0, stretch=False)
  table.tag_configure('oddrow', background="white")
  table.tag_configure('evenrow', background="#e0e0e0")
  table.pack(anchor="w", pady=(0,5))

  for i, (key, match) in enumerate(matches.items()):
    data = (
      match.team1.name if match.team1 is not None else "-",
      match.team2.name if match.team2 is not None else "-",
      match.PrintScore(),
      key,
    )
    if i % 2 == 0:
      tags = ('evenrow',)
    else:
      tags = ('oddrow',)
    table.insert(parent='', index='end', values=data, tags=tags)

  def UpdateScore(_):
    selectedItems = table.selection()
    if len(selectedItems) != 1:
      messagebox.showwarning("Aviso", "Só é possível atualizar um item por vez.")
    else:
      values = table.item(selectedItems[0])["values"]
      key = values[3]
      match = matches[key]
      OpenScoreWindow(app, category, match)
  table.bind("<F2>", UpdateScore)