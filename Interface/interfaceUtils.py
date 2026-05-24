import tkinter as tk
from tkinter import ttk
from tournament import Tournament
import theme


def ClearFrame(frame:tk.Frame):
  for widget in frame.winfo_children():
    widget.destroy()


def CreateCategoriesComboBox(parentFrame:tk.Frame, tournament:Tournament, categoryName=None, isBackGroundWhite=True) -> ttk.Combobox:
  tk.Label(parentFrame, text="Selecione a categoria", font=theme.FONT_SMALL, bg=theme.BG,
           fg=theme.TEXT_MUTED).pack(anchor="w", padx=10, pady=(16,4))
  categoriesNames = [c for c in tournament.categories]
  combo =  ttk.Combobox(
    parentFrame,
    values=categoriesNames,
    state="readonly",
    width=30,
    font=('Segoe UI', 12),
  )
  if categoryName is None:
    categoryName = categoriesNames[0]
  combo.set(categoryName)
  combo.pack(anchor="w", padx=10)
  return combo