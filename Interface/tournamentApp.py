import tkinter as tk
from tkinter import ttk

from tkinter import messagebox, filedialog

from tennisEnums import MatchTypes, CategoryTypes
from tournament import Tournament
from category import Category
from fileReader import ReadInputFile
from fileSave import SaveFile

from interfaceUtils import CreateCategoriesComboBox
from newTournamentWindow import OpenNewTournamentWindow
from newCategoryWindow import OpenNewCategoryWindow
from newTeamWindow import OpenTeamWindow
from changeCategoryWindow import OpenChangeCategoryWindow
from matchesTable import CreateMatchesTable
from tennisHelper import GetMaximumStage


class TournamentApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("Gerenciador de Torneios de Tênis")
    self.state("zoomed")

    self.columnconfigure(1, weight=1)  # área do conteúdo expande
    self.rowconfigure(0, weight=1)

    self.CreateSidebar()
    self.CreateContentArea()

    self.tournament: Tournament|None = None

    self.UpdateTournamentContent()

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))


  def OpenTournament(self):
    filePath = filedialog.askopenfilename(
      title = "Selecione um arquivo",
      filetypes = [("Text files", "*.txt")],
    )
    if filePath != '':
      self.tournament = ReadInputFile(filePath)
      self.UpdateTournamentContent()


  def SaveTournament(self):
    filePath = filedialog.asksaveasfilename(
      title="Salvar arquivo como",
      defaultextension=".txt",
      filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
    )
    if filePath != '':
      SaveFile(filePath, self.tournament)


  def CreateSidebar(self):
    sidebar = tk.Frame(self, bg="#2c3e50", padx=20, pady=20)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)

    menuItems = ["Torneio", "Categorias", "Jogadores", "Duplas", "Duplas Antigas", "Jogos", "Salvar Torneio"]

    for item in menuItems:
      if item == "Salvar Torneio":
        btn = tk.Button(
          sidebar,
          text=item,
          font=("Arial", 12),
          fg="white",
          bg="#2c3e50",
          bd=0,
          relief="flat",
          activebackground="#16a085",
          activeforeground="white",
          command=lambda: self.SaveTournament()
        )
      else:
        btn = tk.Button(
          sidebar,
          text=item,
          font=("Arial", 12),
          fg="white",
          bg="#2c3e50",
          bd=0,
          relief="flat",
          activebackground="#16a085",
          activeforeground="white",
          command=lambda i=item: self.ShowContent(i)
        )

      pady = (2,40) if item == "Jogos" else (2,2)
      btn.pack(fill="x", pady=pady)


  def CreateContentArea(self):
    container = tk.Frame(self, bg="white")
    container.grid(row=0, column=1, sticky="nsew")

    canvas = tk.Canvas(container, bg="white", highlightthickness=0)
    vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    self.contentFrame = tk.Frame(canvas, bg="white")
    self.contentFrame_id = canvas.create_window((0, 0), window=self.contentFrame, anchor="nw")
    def onConfigure(event):
      canvas.configure(scrollregion=canvas.bbox("all"))
      canvas.itemconfig(self.contentFrame_id, width=canvas.winfo_width())
    self.contentFrame.bind("<Configure>", onConfigure)

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
      canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    canvas.bind_all("<MouseWheel>", onMousewheel)


  def ClearContent(self):
    for widget in self.contentFrame.winfo_children():
      widget.destroy()


  def UpdateTournamentContent(self):
    self.ClearContent()
    tk.Label(self.contentFrame, text="Informações do Torneio", font=("Arial", 28), bg="white").pack(padx=10, pady=20, anchor="w")
    if self.tournament is None:
      tk.Label(self.contentFrame, text="Nenhum torneio carregado!", font=('Arial, 18'), bg='white').pack(anchor="w", padx=10, pady=5)
    else:
      tournamentName = self.tournament.name
      numberOfSets = str(self.tournament.sets)
      setType = self.tournament.setType.name
      lastSetType = self.tournament.lastSetType.name

      tk.Label(self.contentFrame, text=f"Nome do Torneio: {tournamentName}", font=('Arial, 12'), bg='white').pack(anchor="w", padx=10, pady=5)
      tk.Label(self.contentFrame, text=f"Quantidade de Sets: {numberOfSets}", font=('Arial, 12'), bg='white').pack(anchor="w", padx=10, pady=(20,5))
      tk.Label(self.contentFrame, text=f"Tipo de Set: {setType}", font=('Arial, 12'), bg='white').pack(anchor="w", padx=10, pady=(20,5))
      tk.Label(self.contentFrame, text=f"Tipo do último Set: {lastSetType}", font=('Arial, 12'), bg='white').pack(anchor="w", padx=10, pady=(20,5))

    button = tk.Button(
      self.contentFrame,
      text="Criar Torneio",
      command=self.OpenNewTournamentWindow,
      font=('Arial, 12'),
    )
    button.pack(anchor="w", padx=10, pady=(20,5))

    tk.Button(
      self.contentFrame,
      text="Abrir Torneio",
      command=lambda: self.OpenTournament(),
      font=('Arial, 12'),
    ).pack(anchor="w", padx=10, pady=(20,5))


  def UpdateTeamsTables(self, categoryName, isDoublesPage=False):
    for widget in self.contentFrame.winfo_children():
      if (isinstance(widget, ttk.Treeview)) or (isinstance(widget, tk.Button)):
        widget.destroy()

    table = ttk.Treeview(self.contentFrame, columns=('name', 'seedNumber'), show="headings")
    table.heading('name', text="Nome")
    table.heading('seedNumber', text="Nº Cabeça de Chave")
    table.column('name', width=250, anchor="w")
    table.column('seedNumber', width=250, anchor="center")
    table.tag_configure('oddrow', background="white")
    table.tag_configure('evenrow', background="#e0e0e0")
    table.pack(anchor="w", padx=10, pady=20, fill="y", expand=True)

    category = self.tournament.GetCategory(categoryName)
    category.SortTeams()
    teams = category.teams
    if (category.matchType is MatchTypes.Double) and (not isDoublesPage):
      teams = category.players
    elif (category.matchType is MatchTypes.Single) and (isDoublesPage):
      teams = {}

    for i, team in enumerate(teams.values()):
      data = (
        team.name,
        str(team.seedNumber),
      )
      if i % 2 == 0:
        tags = ('evenrow',)
      else:
        tags = ('oddrow',)
      table.insert(parent='', index='end', values=data, tags=tags)

    def DeleteSelectedItems(_):
      selectedItems = table.selection()
      if not selectedItems:
        return
      if messagebox.askyesno("Confirmação", "Deseja realmente excluir os itens selecionados?"):
        for item in selectedItems:
          teamName = table.item(item)["values"][0]
          teams.pop(teamName)
          table.delete(item)
      self.UpdateTeamsTables(categoryName, isDoublesPage)
    table.bind("<Delete>", DeleteSelectedItems)

    def UpdateTeam(_):
      selectedItems = table.selection()
      if len(selectedItems) != 1:
        messagebox.showwarning("Aviso", "Só é possível atualizar um item por vez.")
      else:
        OpenTeamWindow(self, categoryName, isDoublesPage, True, table.item(selectedItems[0])["values"])
    table.bind("<F2>", UpdateTeam)

    def ChangeSeedNumbers(_):
      selectedItems = table.selection()
      seedNumbers = set()
      for item in selectedItems:
        seedNumber = table.item(item)["values"][1]
        seedNumbers.add(int(seedNumber))
      if len(seedNumbers) != 2:
        messagebox.showwarning("Aviso", "Só é possível atualizar um conjunto de itens que possuam exatamente dois números de cabeça de chave distintos.")
      else:
        seedNumbers = list(seedNumbers)
        change = {
          seedNumbers[0]: seedNumbers[1],
          seedNumbers[1]: seedNumbers[0],
        }
        for item in selectedItems:
          teamName = table.item(item)["values"][0]
          newSeedNumber = change[table.item(item)["values"][1]]
          teams[teamName].seedNumber = newSeedNumber
      self.UpdateTeamsTables(categoryName, isDoublesPage)
    table.bind("<F3>", ChangeSeedNumbers)

    def ChangeCategory(_):
      OpenChangeCategoryWindow(self, categoryName, teams, isDoublesPage, table)
    table.bind("<F4>", ChangeCategory)

    tk.Button(
      self.contentFrame,
      text="Adicionar",
      command=lambda: OpenTeamWindow(self, categoryName, isDoublesPage),
      font=('Arial, 12'),
    ).pack(anchor="w", padx=10, pady=(5,5))


  def UpdateOldDoublesContent(self):
    table = ttk.Treeview(self.contentFrame, columns=('player1', 'player2'), show="headings")
    table.heading('player1', text="Jogador 1")
    table.heading('player2', text="Jogador 2")
    table.column('player1', width=250, anchor="w")
    table.column('player2', width=250, anchor="w")
    table.tag_configure('oddrow', background="white")
    table.tag_configure('evenrow', background="#e0e0e0")
    table.pack(anchor="w", padx=10, pady=20, fill="y", expand=True)

    for i, double in enumerate(self.tournament.oldDoubles):
      data = (
        double[0],
        double[1],
      )
      if i % 2 == 0:
        tags = ('evenrow',)
      else:
        tags = ('oddrow',)
      table.insert(parent='', index='end', values=data, tags=tags)


  def UpdateMatchesContent(self, categoryName=None):
    if categoryName is None:
      categoryName = next(iter(self.tournament.categories))
    category = self.tournament.GetCategory(categoryName)
    category.SortMatches()

    self.ClearContent()

    combo = CreateCategoriesComboBox(self.contentFrame, self.tournament, categoryName)
    combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateMatchesContent(event.widget.get()))

    if category.matchType == MatchTypes.Single:
      teamStr = "Jogador"
    else:
      teamStr = "Dupla"

    eliminationTitles = {
      1: 'Final:',
      2: 'Semifinais:',
      4: 'Quartas de Final:',
      8: 'Oitavas de Final:',
    }

    if (category.categoryType == CategoryTypes.Groups) or (category.categoryType == CategoryTypes.SingleElimination):
      if category.categoryType == CategoryTypes.Groups:
        for i in range(len(category.groups)):
          key = str(i+1).zfill(3) + 'GR'
          matches = category.GetMatches(key)
          CreateMatchesTable(self, category, matches, teamStr, f"Grupo {i+1}:")

      stage = GetMaximumStage(list(category.matches.keys()))
      if stage is None:
        stage = 0
      while stage >= 1:
        key = str(stage).zfill(3) + "FP"
        matches = category.GetMatches(key)
        CreateMatchesTable(self, category, matches, teamStr, eliminationTitles.get(stage, 'Fase Eliminatória:'))
        stage = int(stage/2)

    else:
      if category.categoryType == CategoryTypes.RoundRobin:
        title = "Grupo Único:"
      else:
        title = ''
      CreateMatchesTable(self, category, category.matches, teamStr, title)


  def OpenNewTournamentWindow(self):
    OpenNewTournamentWindow(self)


  def StartCategory(self, category:Category):
    if category.isInitialized:
      messagebox.showwarning("Aviso", "Categoria já iniciada. Não é possível iniciá-la novamente.")
      return

    isConfirmed = messagebox.askyesno("Confirmação", f"Deseja realmente iniciar a categoria {category.name}?")
    if isConfirmed:
      self.tournament.StartCategory(category.name)
      self.UpdateCategories(category.name)


  def DeleteCategory(self, category:Category):
    isConfirmed = messagebox.askyesno("Confirmação", f"Deseja realmente excluir a categoria {category.name}?")
    if not isConfirmed:
      return

    self.tournament.categories.pop(category.name)
    if len(self.tournament.categories) > 0:
      categoryName = next(iter(self.tournament.categories))
    else:
      categoryName = ""
    self.UpdateCategories(categoryName)


  def UpdateCategories(self, categoryName):
    self.ClearContent()
    category = None
    if self.tournament is None:
      tk.Label(self.contentFrame, text="Nenhum torneio carregado!", font=('Arial', 20), bg='white').pack(anchor="w", padx=10, pady=(15,5))
    elif len(self.tournament.categories) == 0:
      tk.Label(self.contentFrame, text="Nenhuma categoria criada!", font=('Arial', 20), bg='white').pack(anchor="w", padx=10, pady=(15,5))
    else:
      category = self.tournament.GetCategory(categoryName)
      if category is None:
        tk.Label(self.contentFrame, text="Nenhuma categoria selecionada!", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=(15,5))
      else:
        combo = CreateCategoriesComboBox(self.contentFrame, self.tournament, categoryName)
        combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateCategories(event.widget.get()))

        tk.Label(self.contentFrame, text=f"Categoria {category.name}:", font=('Arial', 12, 'bold'), bg='white').pack(anchor="w", padx=10, pady=(15,5))
        tk.Label(self.contentFrame, text=f"Tipo: {category.categoryType.name}", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=5)
        tk.Label(self.contentFrame, text=f"Simples ou duplas: {category.matchType.name}", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=5)
        tk.Label(self.contentFrame, text=f"Categoria inicializada? {category.isInitialized}", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=5)
        tk.Label(self.contentFrame, text=f"Grupos finalizados? {category.isGroupsFinished}", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=5)
        tk.Label(self.contentFrame, text=f"Duplas sorteadas? {category.isRandomDoubles}", font=('Arial', 12), bg='white').pack(anchor="w", padx=10, pady=5)

    if category is not None:
      button = tk.Button(
        self.contentFrame,
        text="Iniciar categoria",
        command=lambda: self.StartCategory(category),
        font=('Arial, 12'),
      )
      button.pack(anchor="w", padx=10, pady=(20,5))

    if self.tournament is not None:
      button = tk.Button(
        self.contentFrame,
        text="Criar categoria",
        command=lambda: OpenNewCategoryWindow(self),
        font=('Arial, 12'),
      )
      button.pack(anchor="w", padx=10, pady=(20,5))

    if category is not None:
      button = tk.Button(
        self.contentFrame,
        text="Excluir categoria",
        command=lambda: self.DeleteCategory(category),
        font=('Arial, 12'),
      )
      button.pack(anchor="w", padx=10, pady=(20,5))


  def ShowContent(self, menuItem):
    for widget in self.contentFrame.winfo_children():
      widget.destroy()

    if menuItem == "Torneio":
      self.UpdateTournamentContent()

    elif menuItem == "Categorias":
      if self.tournament is None or len(self.tournament.categories) == 0:
        categoryName = ""
      else:
        categoryName = next(iter(self.tournament.categories))
      self.UpdateCategories(categoryName)

    elif (menuItem == "Jogadores") or (menuItem == "Duplas"):
      if self.tournament is not None:
        if len(self.tournament.categories) > 0:
          combo = CreateCategoriesComboBox(self.contentFrame, self.tournament)
          if menuItem == "Jogadores":
            combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateTeamsTables(event.widget.get()))
            self.UpdateTeamsTables(combo['values'][0])
          else:
            combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateTeamsTables(event.widget.get(), True))
            self.UpdateTeamsTables(combo['values'][0], True)
        else:
          tk.Label(self.contentFrame, text=f"Nenhuma categoria criada!", font=('Arial, 16'), bg='white').pack(anchor="w", padx=10, pady=5)
      else:
        tk.Label(self.contentFrame, text="Nenhum torneio carregado!", font=('Arial', 20), bg='white').pack(anchor="w", padx=10, pady=(15,5))

    elif menuItem == "Duplas Antigas":
      self.UpdateOldDoublesContent()

    elif menuItem == "Jogos":
      if self.tournament is not None:
        if len(self.tournament.categories) > 0:
          self.UpdateMatchesContent()
        else:
          tk.Label(self.contentFrame, text=f"Nenhuma categoria criada!", font=('Arial, 16'), bg='white').pack(anchor="w", padx=10, pady=5)
      else:
        tk.Label(self.contentFrame, text="Nenhum torneio carregado!", font=('Arial', 20), bg='white').pack(anchor="w", padx=10, pady=(15,5))



if __name__ == "__main__":
  app = TournamentApp()
  app.mainloop()
