from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import messagebox

from resultPointsSelector import ResultPointsSelector


def UpdateResultPoints(app: "TournamentApp", window: tk.Toplevel, pointsSelector: ResultPointsSelector):
  try:
    app.tournament.resultPoints = pointsSelector.GetResultPoints()
  except Exception as e:
    messagebox.showerror("Erro", str(e))
    return

  window.destroy()
  app.UpdateTournamentContent()


def OpenUpdateResultPointsWindow(app: "TournamentApp"):
  if app.tournament is None:
    messagebox.showwarning("Aviso", "Nenhum torneio carregado.")
    return

  window = tk.Toplevel(app)
  window.title("Atualizar Pontuação por Resultado")
  window.geometry("600x500")

  tk.Label(window, text="Pontuação por Resultado", font=("Arial", 20)).pack(padx=10, pady=20, anchor="w")

  pointsSelector = ResultPointsSelector(window, app.tournament.sets, app.tournament.resultPoints)

  tk.Button(
    window,
    text="Atualizar",
    command=lambda: UpdateResultPoints(app, window, pointsSelector),
    font=('Arial', 12),
  ).pack(anchor="w", padx=10, pady=(20, 5))
