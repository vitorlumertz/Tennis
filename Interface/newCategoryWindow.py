from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tennisEnums import MatchTypes, CategoryTypes, GroupClassificationTypes
from category import Category


def CreateCategory(
  app: "TournamentApp",
  window: tk.Toplevel,
  categoryName: str,
  categoryType: CategoryTypes,
  matchType: MatchTypes,
  isRandomDoubles: str,
  groupClassificationType: GroupClassificationTypes,
  numOfclassifiedsInGroups: int,
):
  if categoryName.replace(' ', '') == '':
    messagebox.showerror("Erro", "Não é possível criar uma categoria com nome vazio.")
    window.destroy()
    return

  isRandomDoubles = True if isRandomDoubles == 'Sim' else False

  if groupClassificationType == GroupClassificationTypes.TotalNumber:
    if numOfclassifiedsInGroups <= 0:
      messagebox.showerror("Erro", "Informe um número válido de classificados para o tipo TotalNumber.")
      return

  category = Category(
    name = categoryName,
    categoryType = categoryType,
    matchType = matchType,
    isRandomDoubles = isRandomDoubles,
    groupClassificationType = groupClassificationType,
    numOfclassifiedsInGroups = numOfclassifiedsInGroups if groupClassificationType == GroupClassificationTypes.TotalNumber else 0,
  )
  try:
    app.tournament.AddCategory(category)
  except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível criar a categoria!\n\n{e}")
    window.destroy()
  app.UpdateCategories(categoryName)


def OpenNewCategoryWindow(app:"TournamentApp"):
  window = tk.Toplevel(app)
  window.title("Nova Categoria")
  window.geometry("600x650")

  tk.Label(window, text="Configure a Nova Categoria", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome da Categoria:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(window, width=50, font=('Arial', 12))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  options = [categoryType.name for categoryType in CategoryTypes]
  categoryType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=categoryType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Simples ou Duplas:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  options = [matchType.name for matchType in MatchTypes]
  matchType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=matchType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Sortear Duplas?", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  options = ['Sim', 'Não']
  isRandomDoubles = tk.StringVar(value=options[1])
  combo = ttk.Combobox(
    window,
    textvariable=isRandomDoubles,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo de classificação dos grupos:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  groupClassificationOptions = [groupClassificationType.name for groupClassificationType in GroupClassificationTypes]
  groupClassificationType = tk.StringVar(value=groupClassificationOptions[0])
  ttk.Combobox(
    window,
    textvariable=groupClassificationType,
    values=groupClassificationOptions,
    state="readonly",
    width=30,
    font=('Arial', 12),
  ).pack(anchor="w", padx=10)

  tk.Label(window, text="Número de classificados:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  numClassifiedsEntry = tk.Entry(window, width=50, font=('Arial', 12))
  numClassifiedsEntry.pack(anchor="w", padx=10)
  numClassifiedsEntry.insert(0, "0")

  def OnCreateCategory():
    try:
      numOfclassifiedsInGroups = int(numClassifiedsEntry.get())
    except ValueError:
      messagebox.showerror("Erro", "Informe um número inteiro válido para a quantidade de classificados.")
      return

    CreateCategory(
      app,
      window,
      nameEntry.get(),
      CategoryTypes[categoryType.get()],
      MatchTypes[matchType.get()],
      isRandomDoubles.get(),
      GroupClassificationTypes[groupClassificationType.get()],
      numOfclassifiedsInGroups,
    )

  tk.Button(
    window,
    text="Criar Categoria",
    command=OnCreateCategory,
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(20,5))
