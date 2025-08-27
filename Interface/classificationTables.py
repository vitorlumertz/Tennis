from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk

from match import Match


def CreateGroupClassificationTable(app:"TournamentApp", classification:dict[str, Match], labelTitle:str=''):
  style = ttk.Style()
  style.configure("Classification.Treeview", font=("Arial", 12))
  style.configure("Classification.Treeview.Heading", font=("Arial", 12, "bold"))

  frame = tk.Frame(app.contentFrame, bg="white")
  frame.pack(anchor="w", padx=10, pady=10)
  if labelTitle != '':
    tk.Label(frame, text=labelTitle, font=("Arial", 12), bg="white").pack(pady=(0,2), anchor="w")
  table = ttk.Treeview(frame, columns=('teamName', 'victories', 'setBalance', 'gameBalance'), show="headings", height=len(classification), style="Classification.Treeview")
  table.heading('teamName', text="Nome")
  table.heading('victories', text="Vitórias")
  table.heading('setBalance', text="Saldo Sets")
  table.heading('gameBalance', text="Saldo Games")
  table.column('teamName', width=300, anchor="center")
  table.column('victories', width=150, anchor="center")
  table.column('setBalance', width=150, anchor="center")
  table.column('gameBalance', width=150, anchor="center")
  table.tag_configure('oddrow', background="white")
  table.tag_configure('evenrow', background="#e0e0e0")
  table.pack(anchor="w", pady=(0,5))

  for i, (teamName, values) in enumerate(classification.items()):
    data = (
      teamName,
      values["Victories"],
      values["SetBalance"],
      values["GameBalance"],
    )
    if i % 2 == 0:
      tags = ('evenrow',)
    else:
      tags = ('oddrow',)
    table.insert(parent='', index='end', values=data, tags=tags)