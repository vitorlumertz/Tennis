import tkinter as tk
from tkinter import ttk
from tennis_manager.tournament import Tournament


def ClearFrame(frame:tk.Frame):
  for widget in frame.winfo_children():
    widget.destroy()


def BindMousewheelToCanvas(canvas:tk.Canvas, scrollArea:tk.Misc=None):
  if scrollArea is None:
    scrollArea = canvas

  def isWidgetInside(widget, parent):
    while widget is not None:
      if widget == parent:
        return True
      widget = widget.master
    return False

  def onMousewheel(event):
    try:
      first, last = canvas.yview()
    except tk.TclError:
      canvas.unbind_all("<MouseWheel>")
      return

    if event.num == 4 or event.delta > 0:
      if first <= 0:
        return
      canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
      if last >= 1:
        return
      canvas.yview_scroll(1, "units")

  def bindMousewheel(_event):
    canvas.bind_all("<MouseWheel>", onMousewheel)

  def unbindMousewheel(_event):
    widgetUnderMouse = canvas.winfo_containing(canvas.winfo_pointerx(), canvas.winfo_pointery())
    if isWidgetInside(widgetUnderMouse, canvas) or isWidgetInside(widgetUnderMouse, scrollArea):
      return
    canvas.unbind_all("<MouseWheel>")

  def onDestroy(event):
    if event.widget == canvas:
      canvas.unbind_all("<MouseWheel>")

  canvas.bind("<Enter>", bindMousewheel)
  canvas.bind("<Leave>", unbindMousewheel)
  scrollArea.bind("<Enter>", bindMousewheel)
  scrollArea.bind("<Leave>", unbindMousewheel)
  canvas.bind("<Destroy>", onDestroy)


def CreateScrollableFrame(parent:tk.Misc) -> ttk.Frame:
  canvas = tk.Canvas(parent)
  canvas.pack(side="left", fill="both", expand=True)

  scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
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

  BindMousewheelToCanvas(canvas, content)

  return content


def CreateCategoriesComboBox(parentFrame:tk.Frame, tournament:Tournament, categoryName=None, isBackGroundWhite=True) -> ttk.Combobox:
  if isBackGroundWhite:
    tk.Label(parentFrame, text="Selecione a Categoria:", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=(20,5))
  else:
    tk.Label(parentFrame, text="Selecione a Categoria:", font=('Arial', 12)).pack(anchor="w", padx=10, pady=(20,5))
  categoriesNames = [c for c in tournament.categories]
  combo =  ttk.Combobox(
    parentFrame,
    values=categoriesNames,
    state="readonly",
    width=30,
    font=('Arial', 12),
  )
  if categoryName is None:
    categoryName = categoriesNames[0]
  combo.set(categoryName)
  combo.pack(anchor="w", padx=10)
  return combo
