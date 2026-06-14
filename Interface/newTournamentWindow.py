from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from classification import Columns, ResultPoints
from tournament import Tournament
from tennisEnums import SetTypes
from classificationCriteriaSelector import ClassificationCriteriaSelector
from resultPointsSelector import ResultPointsSelector


def CreateTournament(
  app:"TournamentApp",
  window:tk.Toplevel,
  tournamentName:str,
  numberOfSets:int,
  setType:SetTypes,
  lastSetType:SetTypes,
  classificationCriteria:list[Columns],
  resultPoints:ResultPoints,
):
  if tournamentName.replace(' ', '') == '':
    messagebox.showerror("Erro", "Não é possível criar um torneio com nome vazio.")
    window.destroy()
    return

  isConfirmed = messagebox.askyesno("Confirmação", "Deseja realmente criar um novo torneio?\nO torneio atual será perdido.")

  if len(classificationCriteria) == 0:
    messagebox.showerror("Erro", "Selecione ao menos um critério de desempate.")
    return

  if isConfirmed:
    app.tournament = Tournament(
      name = tournamentName,
      sets = numberOfSets,
      setType = setType,
      lastSetType = lastSetType,
      classificationCriteria = classificationCriteria,
      resultPoints = resultPoints,
    )
    app.UpdateTournamentContent()
  else:
    messagebox.showinfo("Cancelado", "Operação cancelada.")

  window.destroy()


def OpenNewTournamentWindow(app:"TournamentApp"):
  window = tk.Toplevel(app)
  window.title("Novo Torneio")
  window.geometry("600x650")

  canvas = tk.Canvas(window)
  canvas.pack(side="left", fill="both", expand=True)

  scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
  scrollbar.pack(side="right", fill="y")

  canvas.configure(yscrollcommand=scrollbar.set)

  content = ttk.Frame(canvas)

  canvasWindow = canvas.create_window((0, 0), window=content, anchor="nw")

  def onFrameConfigure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
  content.bind("<Configure>", onFrameConfigure)

  def onCanvasConfigure(event):
    canvas.itemconfigure(canvasWindow, width=event.width)
  canvas.bind("<Configure>", onCanvasConfigure)

  def onMousewheel(event):
    first, last = canvas.yview()
    if event.num == 4 or event.delta > 0:
      if first <= 0:
        return
      canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
      if last >= 1:
        return
      canvas.yview_scroll(1, "units")
  canvas.bind_all("<MouseWheel>", onMousewheel)

  tk.Label(content, text="Configure o Novo Torneio", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(content, text="Nome do Torneio:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(content, width=50, font=('Arial', 12))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(content, text="Quantidade de Sets:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  options = ["1", "3", "5"]
  numberOfSets = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    content,
    textvariable=numberOfSets,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)
  setsCombo = combo

  tk.Label(content, text="Tipo de Set:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  options = [setType.name for setType in SetTypes]
  setType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    content,
    textvariable=setType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(content, text="Tipo do último Set:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  lastSetType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    content,
    textvariable=lastSetType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  combo.pack(anchor="w", padx=10)

  criteriaSelector = ClassificationCriteriaSelector(content)
  pointsSelector = ResultPointsSelector(content, int(numberOfSets.get()))

  def UpdateResultPoints(_event=None):
    pointsSelector.SetSets(int(numberOfSets.get()))

  setsCombo.bind("<<ComboboxSelected>>", UpdateResultPoints)

  tk.Button(
    content,
    text="Criar Torneio",
    command=lambda: CreateTournament(
      app,
      content,
      nameEntry.get(),
      int(numberOfSets.get()),
      SetTypes[setType.get()],
      SetTypes[lastSetType.get()],
      criteriaSelector.GetCriteria(),
      pointsSelector.GetResultPoints(),
    ),
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(20,5))
