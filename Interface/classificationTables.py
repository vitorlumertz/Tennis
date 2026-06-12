from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import pandas as pd
import tkinter as tk
from tkinter import ttk

from classification import Classification


def ToInt(v):
  return 0 if pd.isna(v) else int(v)


def CreateGroupClassificationTable(app:"TournamentApp", classification:Classification, labelTitle:str=''):
  style = ttk.Style()
  style.configure("Classification.Treeview", font=("Arial", 12))
  style.configure("Classification.Treeview.Heading", font=("Arial", 12, "bold"))

  frame = tk.Frame(app.contentFrame, bg="white")
  frame.pack(anchor="w", padx=10, pady=10)
  if labelTitle != '':
    tk.Label(frame, text=labelTitle, font=("Arial", 12), bg="white").pack(pady=(0,2), anchor="w")

  columns = ["teamName"]
  for criteria in app.tournament.classificationCriteria:
    columns.append(criteria.name)

  table = ttk.Treeview(frame, columns=columns, show="headings", height=len(classification.classification), style="Classification.Treeview")
  table.heading('teamName', text="Nome")
  table.column('teamName', width=300, anchor="center")

  for criteria in app.tournament.classificationCriteria:
    table.heading(criteria.name, text=criteria.name)
    table.column(criteria.name, width=150, anchor="center")

  table.tag_configure('oddrow', background="white")
  table.tag_configure('evenrow', background="#e0e0e0")
  table.pack(anchor="w", pady=(0,5))

  for i, (teamName, row) in enumerate(classification.classification.iterrows()):
    data = [teamName]
    for criteria in app.tournament.classificationCriteria:
      data.append(ToInt(row[criteria.name]))

    if i % 2 == 0:
      tags = ('evenrow',)
    else:
      tags = ('oddrow',)
    table.insert(parent='', index='end', values=data, tags=tags)