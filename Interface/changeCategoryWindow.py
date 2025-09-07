from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from matchTeams import Team
from interfaceUtils import CreateCategoriesComboBox


def ChangeCategories(
  app: "TournamentApp",
  frame: tk.Frame,
  summaryFrame:tk.Frame,
  window: tk.Toplevel,
  categoryName: str,
  categoryComboBox: ttk.Combobox,
  teams: dict[str,Team],
  isDoublesPage: bool,
  table,
):
  newCategory = app.tournament.GetCategory(categoryComboBox.get())
  selectedItems = table.selection()
  for item in selectedItems:
    teamName = table.item(item)["values"][0]
    try:
      team = teams.pop(teamName)
      newCategory.AddTeam(team)
    except Exception as e:
      messagebox.showerror("Erro", f"Não foi possível trocar {teamName} para a categoria {newCategory.name}.\n\n{e}")

  window.destroy()
  app.UpdateTeamsContent(frame, summaryFrame, categoryName, isDoublesPage)


def OpenChangeCategoryWindow(app:"TournamentApp", frame:tk.Frame, summaryFrame:tk.Frame, categoryName:str, teams:dict[str,Team], isDoublesPage:bool, table):
  window = tk.Toplevel(app)
  window.title("Troca de Categoria")
  window.geometry("300x200")

  categoryComboBox = CreateCategoriesComboBox(window, app.tournament, categoryName, False)

  tk.Button(
    window,
    text="Atualizar",
    command=lambda: ChangeCategories(app, frame, summaryFrame, window, categoryName, categoryComboBox, teams, isDoublesPage, table),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(15,5))