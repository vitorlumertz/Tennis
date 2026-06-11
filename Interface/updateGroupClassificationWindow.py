from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from category import Category
from tennisEnums import GroupClassificationTypes, CategoryTypes


def GetGroupClassificationTypeDisplay(category: Category) -> str:
  if category.groupClassificationType is None:
    return "TwoPerGroup (padrão)"
  return category.groupClassificationType.name


def UpdateGroupClassification(
  app: "TournamentApp",
  window: tk.Toplevel,
  category: Category,
  groupClassificationType: GroupClassificationTypes,
  numOfclassifiedsInGroups: int,
):
  if category.isGroupsFinished:
    messagebox.showerror("Erro", "Não é possível alterar a classificação dos grupos após a fase de grupos estar concluída.")
    return

  if groupClassificationType == GroupClassificationTypes.TotalNumber:
    if numOfclassifiedsInGroups <= 0:
      messagebox.showerror("Erro", "Informe um número válido de classificados para o tipo TotalNumber.")
      return
    if category.groups is not None and numOfclassifiedsInGroups < len(category.groups):
      messagebox.showerror(
        "Erro",
        f"O número de classificados ({numOfclassifiedsInGroups}) deve ser maior ou igual ao número de grupos ({len(category.groups)}).",
      )
      return

  category.groupClassificationType = groupClassificationType
  category.numOfclassifiedsInGroups = numOfclassifiedsInGroups if groupClassificationType == GroupClassificationTypes.TotalNumber else 0

  window.destroy()
  app.UpdateCategories(category.name)


def OpenUpdateGroupClassificationWindow(app: "TournamentApp", category: Category):
  if category.categoryType != CategoryTypes.Groups:
    messagebox.showwarning("Aviso", "Esta operação só se aplica a categorias do tipo Groups.")
    return

  if category.isGroupsFinished:
    messagebox.showerror("Erro", "Não é possível alterar a classificação dos grupos após a fase de grupos estar concluída.")
    return

  window = tk.Toplevel(app)
  window.title("Atualizar Classificação dos Grupos")
  window.geometry("600x350")

  tk.Label(window, text="Atualizar Classificação dos Grupos", font=("Arial", 20)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Tipo de classificação dos grupos:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(10, 5))
  options = [groupClassificationType.name for groupClassificationType in GroupClassificationTypes]
  groupClassificationTypeVar = tk.StringVar(
    value=category.groupClassificationType.name if category.groupClassificationType else GroupClassificationTypes.TwoPerGroup.name
  )
  ttk.Combobox(
    window,
    textvariable=groupClassificationTypeVar,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  ).pack(anchor="w", padx=10)

  tk.Label(window, text="Número de classificados:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20, 5))
  numEntry = tk.Entry(window, width=50, font=('Arial', 12))
  numEntry.pack(anchor="w", padx=10)
  numEntry.insert(0, str(category.numOfclassifiedsInGroups))

  def OnUpdate():
    try:
      numOfclassifiedsInGroups = int(numEntry.get())
    except ValueError:
      messagebox.showerror("Erro", "Informe um número inteiro válido para a quantidade de classificados.")
      return

    UpdateGroupClassification(
      app,
      window,
      category,
      GroupClassificationTypes[groupClassificationTypeVar.get()],
      numOfclassifiedsInGroups,
    )

  tk.Button(
    window,
    text="Atualizar",
    command=OnUpdate,
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(20, 5))
