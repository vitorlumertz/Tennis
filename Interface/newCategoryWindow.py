from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tennisEnums import MatchTypes, CategoryTypes
from category import Category


def CreateCategory(app:"TournamentApp", window:tk.Toplevel, categoryName:str, categoryType:CategoryTypes, matchType:MatchTypes, isRandomDoubles:str):
  if categoryName.replace(' ', '') == '':
    messagebox.showerror("Erro", "Não é possível criar uma categoria com nome vazio.")
    window.destroy()
    return

  isRandomDoubles = True if isRandomDoubles == 'Sim' else False
  category = Category(
    name = categoryName,
    categoryType = categoryType,
    matchType = matchType,
    isRandomDoubles = isRandomDoubles,
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
  window.geometry("600x500")

  tk.Label(window, text="Configure a Nova Categoria", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome da Categoria:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = [categoryType.name for categoryType in CategoryTypes]
  categoryType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=categoryType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Simples ou Duplas:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = [matchType.name for matchType in MatchTypes]
  matchType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=matchType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Sortear Duplas?", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = ['Sim', 'Não']
  isRandomDoubles = tk.StringVar(value=options[1])
  combo = ttk.Combobox(
    window,
    textvariable=isRandomDoubles,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Button(
    window,
    text="Criar Categoria",
    command=lambda: CreateCategory(app, window, nameEntry.get(), CategoryTypes[categoryType.get()], MatchTypes[matchType.get()], isRandomDoubles.get()),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(20,5))
