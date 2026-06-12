from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import messagebox

from classificationCriteriaSelector import ClassificationCriteriaSelector


def UpdateClassificationCriteria(app: "TournamentApp", window: tk.Toplevel, criteriaSelector: ClassificationCriteriaSelector):
  criteria = criteriaSelector.GetCriteria()
  if len(criteria) == 0:
    messagebox.showerror("Erro", "Selecione ao menos um critério de desempate.")
    return

  app.tournament.classificationCriteria = criteria
  window.destroy()
  app.UpdateTournamentContent()


def OpenUpdateClassificationCriteriaWindow(app: "TournamentApp"):
  if app.tournament is None:
    messagebox.showwarning("Aviso", "Nenhum torneio carregado.")
    return

  window = tk.Toplevel(app)
  window.title("Atualizar Critérios de Desempate")
  window.geometry("600x400")

  tk.Label(window, text="Critérios de Desempate dos Grupos", font=("Arial", 20)).pack(padx=10, pady=20, anchor="w")

  criteriaSelector = ClassificationCriteriaSelector(window, app.tournament.classificationCriteria)

  tk.Button(
    window,
    text="Atualizar",
    command=lambda: UpdateClassificationCriteria(app, window, criteriaSelector),
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(20, 5))
