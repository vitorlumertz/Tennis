from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from tournamentApp import TournamentApp

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tournament import Tournament
from tennisEnums import SetTypes


def CreateTournament(app:"TournamentApp", window:tk.Toplevel, tournamentName:str, numberOfSets:int, setType:SetTypes, lastSetType:SetTypes):
  if tournamentName.replace(' ', '') == '':
    messagebox.showerror("Erro", "Não é possível criar um torneio com nome vazio.")
    window.destroy()
    return

  isConfirmed = messagebox.askyesno("Confirmação", "Deseja realmente criar um novo torneio?\nO torneio atual será perdido.")

  if isConfirmed:
    app.tournament = Tournament(
      name = tournamentName,
      sets = numberOfSets,
      setType = setType,
      lastSetType = lastSetType,
    )
    app.UpdateTournamentContent()
  else:
    messagebox.showinfo("Cancelado", "Operação cancelada.")

  window.destroy()


def OpenNewTournamentWindow(app:"TournamentApp"):
  window = tk.Toplevel(app)
  window.title("Novo Torneio")
  window.geometry("600x500")

  tk.Label(window, text="Configure o Novo Torneio", font=("Arial", 28)).pack(padx=10, pady=20, anchor="w")

  tk.Label(window, text="Nome do Torneio:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=5)
  nameEntry = tk.Entry(window, width=50, font=('Arial, 12'))
  nameEntry.pack(anchor="w", padx=10)

  tk.Label(window, text="Quantidade de Sets:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = ["1", "3", "5"]
  numberOfSets = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=numberOfSets,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo de Set:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  options = [setType.name for setType in SetTypes]
  setType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=setType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Label(window, text="Tipo do último Set:", font=('Arial, 12')).pack(anchor="w", padx=10, pady=(20,5))
  lastSetType = tk.StringVar(value=options[0])
  combo = ttk.Combobox(
    window,
    textvariable=lastSetType,
    values=options,
    state="readonly",
    width=30,
    font=('Arial, 12'),
  )
  combo.pack(anchor="w", padx=10)

  tk.Button(
    window,
    text="Criar Torneio",
    command=lambda: CreateTournament(app, window, nameEntry.get(), int(numberOfSets.get()), SetTypes[setType.get()], SetTypes[lastSetType.get()]),
    font=('Arial, 12'),
  ).pack(anchor="w", padx=10, pady=(20,5))