import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from classification import (
  Columns,
  CLASSIFICATION_CRITERIA_OPTIONS,
  DEFAULT_CLASSIFICATION_CRITERIA,
  ClassificationCriteriaToString,
)


class ClassificationCriteriaSelector:
  def __init__(self, parent: tk.Misc, initialCriteria: list[Columns] | None = None):
    self.__criteria = list(initialCriteria if initialCriteria is not None else DEFAULT_CLASSIFICATION_CRITERIA)
    self.__ignoreSelection = False

    tk.Label(parent, text="Critérios de desempate (ordem):", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(10, 5))
    self.__displayLabel = tk.Label(parent, text="", font=('Arial', 12))
    self.__displayLabel.pack(anchor="w", padx=10, pady=5)

    self.__comboVar = tk.StringVar()
    self.__combo = ttk.Combobox(
      parent,
      textvariable=self.__comboVar,
      state="readonly",
      width=30,
      font=('Arial', 12),
    )
    self.__combo.pack(anchor="w", padx=10, pady=5)
    self.__combo.bind("<<ComboboxSelected>>", self.__OnCriteriaSelected)

    tk.Button(
      parent,
      text="Remover último critério",
      command=self.__RemoveLast,
      font=('Arial', 12),
    ).pack(anchor="w", padx=10, pady=5)

    self.__RefreshCombo()
    self.__UpdateDisplay()

  def GetCriteria(self) -> list[Columns]:
    return list(self.__criteria)

  def __UpdateDisplay(self) -> None:
    if len(self.__criteria) == 0:
      text = "(nenhum critério selecionado)"
    else:
      text = ClassificationCriteriaToString(self.__criteria)
    self.__displayLabel.config(text=text)

  def __RefreshCombo(self) -> None:
    self.__ignoreSelection = True
    available = [column.name for column in CLASSIFICATION_CRITERIA_OPTIONS if column not in self.__criteria]
    self.__combo['values'] = available
    if available:
      self.__combo.configure(state="readonly")
      self.__comboVar.set(available[0])
    else:
      self.__comboVar.set('')
      self.__combo.configure(state="disabled")
    self.__ignoreSelection = False

  def __OnCriteriaSelected(self, _event=None) -> None:
    if self.__ignoreSelection:
      return

    selectedName = self.__comboVar.get()
    if selectedName == '':
      return

    column = Columns[selectedName]
    if column in self.__criteria:
      messagebox.showwarning("Aviso", "Este critério já foi selecionado.")
      self.__RefreshCombo()
      return

    self.__criteria.append(column)
    self.__UpdateDisplay()
    self.__RefreshCombo()

  def __RemoveLast(self) -> None:
    if len(self.__criteria) == 0:
      return

    self.__criteria.pop()
    self.__UpdateDisplay()
    self.__RefreshCombo()
