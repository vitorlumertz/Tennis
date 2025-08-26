import tkinter as tk
from tkinter import ttk
from tournament import Tournament


def CreateCategoriesComboBox(parentFrame:tk.Frame, tournament:Tournament, categoryName=None, isBackGroundWhite=True) -> ttk.Combobox:
  if isBackGroundWhite:
    tk.Label(parentFrame, text="Selecione a Categoria:", font=('Arial, 12'), bg='white').pack(anchor="w", padx=10, pady=(20,5))
  else:
    tk.Label(parentFrame, text="Selecione a Categoria:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  categoriesNames = [c for c in tournament.categories]
  combo =  ttk.Combobox(
    parentFrame,
    values=categoriesNames,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  if categoryName is None:
    categoryName = categoriesNames[0]
  combo.set(categoryName)
  combo.pack(anchor="w", padx=10)
  return combo