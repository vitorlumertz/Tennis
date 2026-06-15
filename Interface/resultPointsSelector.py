import tkinter as tk

from tennis_manager.classification import GetDefaultResultPoints, GetPossibleSetResults, ResultPoints


class ResultPointsSelector:
  def __init__(self, parent:tk.Misc, sets:int, initialPoints:ResultPoints|None=None):
    self.__frame = tk.Frame(parent)
    self.__variables: dict[tuple[int, int], tk.IntVar] = {}
    self.__initialPoints = initialPoints.copy() if initialPoints is not None else None

    tk.Label(parent, text="Pontuação por resultado:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20, 5))
    self.__frame.pack(anchor="w", padx=10, pady=5)
    self.SetSets(sets)


  def SetSets(self, sets:int) -> None:
    for widget in self.__frame.winfo_children():
      widget.destroy()

    self.__variables = {}
    defaultPoints = GetDefaultResultPoints(sets)
    possibleResults = GetPossibleSetResults(sets)
    points = defaultPoints.copy()
    if self.__initialPoints is not None:
      for result in possibleResults:
        if result in self.__initialPoints:
          points[result] = self.__initialPoints[result]

    for row, result in enumerate(possibleResults):
      setsT1, setsT2 = result
      tk.Label(self.__frame, text=f"{setsT1}x{setsT2}", font=('Arial', 12), width=8, anchor="w").grid(row=row, column=0, sticky="w", pady=2)

      variable = tk.IntVar(value=points[result])
      self.__variables[result] = variable
      tk.Spinbox(
        self.__frame,
        from_=0,
        to=10,
        textvariable=variable,
        width=5,
        font=('Arial', 12),
      ).grid(row=row, column=1, sticky="w", pady=2)


  def GetResultPoints(self) -> ResultPoints:
    resultPoints = {}
    for result, variable in self.__variables.items():
      value = variable.get()
      if value < 0 or value > 10:
        raise ValueError("A pontuação deve estar entre 0 e 10.")
      resultPoints[result] = value
    return resultPoints
