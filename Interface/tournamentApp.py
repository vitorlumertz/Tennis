import tkinter as tk
from tkinter import ttk

from tkinter import messagebox, filedialog

from tennisEnums import MatchTypes, CategoryTypes
from tournament import Tournament
from category import Category
from fileReader import ReadInputFile
from fileSave import SaveFile
from pdfExporter import ExportGroupCategoryToPdf

import theme
from interfaceUtils import CreateCategoriesComboBox, ClearFrame
from newTournamentWindow import OpenNewTournamentWindow
from newCategoryWindow import OpenNewCategoryWindow
from newTeamWindow import OpenTeamWindow
from changeCategoryWindow import OpenChangeCategoryWindow
from playersImportWindow import OpenImportPlayersWindow
from exportTournamentWindow import OpenExportTournamentWindow
from matchesTable import CreateMatchesTable
from classificationTables import CreateGroupClassificationTable
from tennisHelper import GetMaximumStage


class TournamentApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("Gerenciador de Torneios de Tênis")
    theme.setup(self)
    theme.maximize(self)

    self.columnconfigure(1, weight=1)
    self.rowconfigure(0, weight=1)

    self._activeNav = None
    self.navButtons = {}

    self.CreateSidebar()
    self.CreateContentArea()

    self.tournament: Tournament|None = None

    self.UpdateTournamentContent()


  # ----------------------------------------------------------------- actions
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


  # ------------------------------------------------------------------- shell
  def CreateSidebar(self):
    sidebar = tk.Frame(self, bg=theme.SIDEBAR, padx=14, pady=22, width=230)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)

    brand = tk.Frame(sidebar, bg=theme.SIDEBAR)
    brand.pack(fill="x", padx=6, pady=(0, 26))
    tk.Label(brand, text="●", font=(theme.FAMILY, 16), fg=theme.ACCENT, bg=theme.SIDEBAR).pack(side="left")
    tk.Label(brand, text=" TENNIS", font=(theme.FAMILY, 16, "bold"), fg="white", bg=theme.SIDEBAR).pack(side="left")

    sections = ["Torneio", "Categorias", "Jogadores", "Presença", "Duplas", "Duplas Antigas", "Jogos", "Grupos"]
    for item in sections:
      btn = self._navButton(sidebar, item, lambda i=item: self.ShowContent(i))
      self.navButtons[item] = btn
      btn.pack(fill="x", pady=2)

    tk.Frame(sidebar, bg=theme.SIDEBAR, height=24).pack(fill="x")
    theme.make_button(sidebar, "  Salvar torneio", self.SaveTournament, variant="ghost").pack(fill="x", pady=2)


  def _navButton(self, parent, item, command):
    btn = tk.Button(
      parent, text="   " + item, command=command, font=theme.FONT_BUTTON, anchor="w",
      bg=theme.SIDEBAR, fg=theme.SIDEBAR_TXT, activebackground=theme.SIDEBAR_HOV,
      activeforeground="white", relief="flat", bd=0, padx=10, pady=9,
      cursor="hand2", highlightthickness=0,
    )
    btn.bind("<Enter>", lambda e: btn.configure(fg="white") if self._activeNav != item else None)
    btn.bind("<Leave>", lambda e: btn.configure(fg=theme.SIDEBAR_TXT) if self._activeNav != item else None)
    return btn


  def SetActiveNav(self, item):
    self._activeNav = item
    for name, btn in self.navButtons.items():
      if name == item:
        btn.configure(fg="white", bg=theme.SIDEBAR_HOV)
      else:
        btn.configure(fg=theme.SIDEBAR_TXT, bg=theme.SIDEBAR)


  def CreateContentArea(self):
    container = tk.Frame(self, bg=theme.BG)
    container.grid(row=0, column=1, sticky="nsew")

    self.topbar = tk.Frame(container, bg=theme.BG, height=66)
    self.topbar.pack(side="top", fill="x")
    self.topbar.pack_propagate(False)
    self.topbarTitle = tk.Label(self.topbar, text="", font=theme.FONT_SUBTITLE, bg=theme.BG, fg=theme.TEXT)
    self.topbarTitle.pack(side="left", padx=26)
    self.topbarActions = tk.Frame(self.topbar, bg=theme.BG)
    self.topbarActions.pack(side="right", padx=26)
    tk.Frame(container, bg=theme.BORDER, height=1).pack(side="top", fill="x")

    body = tk.Frame(container, bg=theme.BG)
    body.pack(side="top", fill="both", expand=True)

    canvas = tk.Canvas(body, bg=theme.BG, highlightthickness=0)
    vsb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    self.contentFrame = tk.Frame(canvas, bg=theme.BG)
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
    canvas.bind_all("<MouseWheel>", onMousewheel)


  def SetTopbar(self, title, actions=None):
    self.topbarTitle.configure(text=title)
    for w in self.topbarActions.winfo_children():
      w.destroy()
    for text, command, variant in (actions or []):
      theme.make_button(self.topbarActions, text, command, variant=variant).pack(side="left", padx=(8, 0))


  def ClearContent(self):
    ClearFrame(self.contentFrame)


  def GetCategory(self, categoryName=None):
    if categoryName is None:
      categoryName = next(iter(self.tournament.categories))
    return self.tournament.GetCategory(categoryName)


  # ----------------------------------------------------------- UI components
  def _hero(self, title, subtitle="", actions=None):
    card = tk.Frame(self.contentFrame, bg=theme.SURFACE)
    card.pack(fill="x", padx=26, pady=(20, 14))
    inner = tk.Frame(card, bg=theme.SURFACE)
    inner.pack(fill="x", padx=30, pady=26)
    tk.Label(inner, text=title, font=theme.FONT_TITLE, bg=theme.SURFACE, fg=theme.TEXT,
             anchor="w", justify="left").pack(fill="x", anchor="w")
    if subtitle:
      tk.Label(inner, text=subtitle, font=theme.FONT_BODY, bg=theme.SURFACE, fg=theme.TEXT_MUTED,
               anchor="w", justify="left").pack(fill="x", anchor="w", pady=(8, 0))
    if actions:
      row = tk.Frame(inner, bg=theme.SURFACE)
      row.pack(fill="x", anchor="w", pady=(20, 0))
      for text, command, variant in actions:
        theme.make_button(row, text, command, variant=variant).pack(side="left", padx=(0, 10))


  def _section(self, text):
    tk.Label(self.contentFrame, text=text, font=theme.FONT_SUBTITLE, bg=theme.BG, fg=theme.TEXT,
             anchor="w").pack(fill="x", padx=26, pady=(18, 10))


  def _CategoryCard(self, parent, category):
    card = tk.Frame(parent, bg=theme.SURFACE, width=210, height=150, cursor="hand2")
    card.pack_propagate(False)
    pad = tk.Frame(card, bg=theme.SURFACE)
    pad.pack(fill="both", expand=True, padx=18, pady=16)

    name = tk.Label(pad, text=category.name, font=(theme.FAMILY, 14, "bold"), bg=theme.SURFACE,
                    fg=theme.TEXT, anchor="w", justify="left", wraplength=175)
    name.pack(fill="x", anchor="w")
    matchStr = "Duplas" if category.matchType is MatchTypes.Double else "Simples"
    sub = tk.Label(pad, text=f"{category.categoryType.name} · {matchStr}", font=theme.FONT_SMALL,
                   bg=theme.SURFACE, fg=theme.TEXT_MUTED, anchor="w")
    sub.pack(fill="x", anchor="w", pady=(6, 0))
    countWord = "duplas" if category.matchType is MatchTypes.Double else "jogadores"
    count = tk.Label(pad, text=f"{len(category.teams)} {countWord}", font=theme.FONT_SMALL,
                     bg=theme.SURFACE, fg=theme.TEXT_MUTED, anchor="w")
    count.pack(fill="x", anchor="w")
    statusText = "● Iniciada" if category.isInitialized else "○ Não iniciada"
    statusColor = theme.ACCENT if category.isInitialized else theme.TEXT_MUTED
    status = tk.Label(pad, text=statusText, font=theme.FONT_SMALL, bg=theme.SURFACE,
                      fg=statusColor, anchor="w")
    status.pack(side="bottom", fill="x", anchor="w")

    plain = [card, pad, name, sub, count]
    def recolor(bg):
      for w in plain:
        w.configure(bg=bg)
      status.configure(bg=bg)
    card.bind("<Enter>", lambda e: recolor(theme.ELEV))
    card.bind("<Leave>", lambda e: recolor(theme.SURFACE))
    for w in (card, pad, name, sub, count, status):
      w.bind("<Enter>", lambda e: recolor(theme.ELEV))
      w.bind("<Leave>", lambda e: recolor(theme.SURFACE))
      w.bind("<Button-1>", lambda e, n=category.name: self._OpenCategory(n))
    return card


  def _CategoryGrid(self, parent=None):
    parent = parent or self.contentFrame
    grid = tk.Frame(parent, bg=theme.BG)
    grid.pack(fill="x", padx=20, pady=(0, 16))
    cols = 4
    for i, category in enumerate(self.tournament.categories.values()):
      self._CategoryCard(grid, category).grid(row=i // cols, column=i % cols, padx=6, pady=6, sticky="nw")


  def _OpenCategory(self, categoryName):
    self.UpdateCategories(categoryName)


  def _ShowMatchesFor(self, categoryName):
    self.UpdateMatchesContent(categoryName)


  # -------------------------------------------------------------- screens
  def UpdateTournamentContent(self):
    self.ClearContent()
    self.SetActiveNav("Torneio")

    if self.tournament is None:
      self.SetTopbar("Início")
      self._hero(
        "Nenhum torneio carregado",
        "Crie um novo torneio ou abra um arquivo existente para começar.",
        [("Criar torneio", self.OpenNewTournamentWindow, "primary"),
         ("Abrir torneio", self.OpenTournament, "ghost")],
      )
      return

    t = self.tournament
    self.SetTopbar("Início", [
      ("Importar Sheets", self.OpenImportPlayersWindow, "ghost"),
      ("Exportar Sheets", self.OpenExportTournamentWindow, "ghost"),
    ])
    subtitle = f"Melhor de {t.sets} sets  ·  {t.setType.name}  ·  último set: {t.lastSetType.name}"
    self._hero(t.name, subtitle, [
      ("Salvar torneio", self.SaveTournament, "primary"),
      ("Abrir outro", self.OpenTournament, "ghost"),
      ("Novo torneio", self.OpenNewTournamentWindow, "ghost"),
    ])

    self._section("Categorias")
    if len(t.categories) == 0:
      tk.Label(self.contentFrame, text="Nenhuma categoria ainda.", font=theme.FONT_BODY,
               bg=theme.BG, fg=theme.TEXT_MUTED, anchor="w").pack(fill="x", padx=26)
      theme.make_button(self.contentFrame, "+ Nova categoria",
                        lambda: OpenNewCategoryWindow(self), "primary").pack(anchor="w", padx=26, pady=12)
    else:
      self._CategoryGrid()
      theme.make_button(self.contentFrame, "+ Nova categoria",
                        lambda: OpenNewCategoryWindow(self), "ghost").pack(anchor="w", padx=26, pady=(2, 20))


  def UpdateCategories(self, categoryName):
    self.ClearContent()
    self.SetActiveNav("Categorias")

    if self.tournament is None:
      self.SetTopbar("Categorias")
      self._hero("Nenhum torneio carregado", "Crie ou abra um torneio primeiro.",
                 [("Ir para Início", self.UpdateTournamentContent, "primary")])
      return

    if len(self.tournament.categories) == 0:
      self.SetTopbar("Categorias")
      self._hero("Nenhuma categoria", "Crie a primeira categoria do torneio.",
                 [("+ Nova categoria", lambda: OpenNewCategoryWindow(self), "primary")])
      return

    self.SetTopbar("Categorias", [("+ Nova categoria", lambda: OpenNewCategoryWindow(self), "ghost")])

    category = self.tournament.GetCategory(categoryName) if categoryName else None
    if category is None:
      self._section("Selecione uma categoria")
      self._CategoryGrid()
      return

    switcher = tk.Frame(self.contentFrame, bg=theme.BG)
    switcher.pack(fill="x", padx=16, pady=(8, 0))
    combo = CreateCategoriesComboBox(switcher, self.tournament, categoryName)
    combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateCategories(event.widget.get()))

    matchStr = "Duplas" if category.matchType is MatchTypes.Double else "Simples"
    flags = ["Iniciada" if category.isInitialized else "Não iniciada"]
    if category.isRandomDoubles:
      flags.append("Duplas sorteadas")
    if category.isGroupsFinished:
      flags.append("Grupos finalizados")
    subtitle = f"{category.categoryType.name}  ·  {matchStr}  ·  " + "  ·  ".join(flags)
    self._hero(f"Categoria {category.name}", subtitle, [
      ("▶ Iniciar categoria", lambda: self.StartCategory(category), "primary"),
      ("Ver jogos", lambda: self._ShowMatchesFor(category.name), "ghost"),
      ("Exportar PDF", lambda: self.ExportPdf(category), "ghost"),
      ("Excluir", lambda: self.DeleteCategory(category), "ghost"),
    ])

    self._section("Todas as categorias")
    self._CategoryGrid()


  def UpdateTeamsTables(self, frame:tk.Frame, summaryFrame:tk.Frame, categoryName, isDoublesPage=False):
    for widget in frame.winfo_children():
      if (isinstance(widget, ttk.Treeview)) or (isinstance(widget, tk.Button)):
        widget.destroy()

    category = self.tournament.GetCategory(categoryName)
    category.SortTeams()
    teams = category.teams
    if (category.matchType is MatchTypes.Double) and (not isDoublesPage):
      teams = category.players
    elif (category.matchType is MatchTypes.Single) and (isDoublesPage):
      teams = {}

    table = ttk.Treeview(frame, columns=('name', 'seedNumber'), show="headings", height=len(teams))
    table.heading('name', text="Nome")
    table.heading('seedNumber', text="Nº Cabeça de Chave")
    table.column('name', width=250, anchor="w")
    table.column('seedNumber', width=250, anchor="center")
    table.tag_configure('oddrow', background=theme.SURFACE)
    table.tag_configure('evenrow', background=theme.ROW_ALT)
    table.pack(anchor="w", padx=10, pady=20, fill="y", expand=True)

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
      self.UpdateTeamsContent(frame, summaryFrame, categoryName, isDoublesPage)
    table.bind("<Delete>", DeleteSelectedItems)

    def UpdateTeam(_):
      selectedItems = table.selection()
      if len(selectedItems) != 1:
        messagebox.showwarning("Aviso", "Só é possível atualizar um item por vez.")
      else:
        OpenTeamWindow(self, frame, summaryFrame, categoryName, isDoublesPage, True, table.item(selectedItems[0])["values"])
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
      self.UpdateTeamsContent(frame, summaryFrame, categoryName, isDoublesPage)
    table.bind("<F3>", ChangeSeedNumbers)

    def ChangeCategory(_):
      OpenChangeCategoryWindow(self, frame, summaryFrame, categoryName, teams, isDoublesPage, table)
    table.bind("<F4>", ChangeCategory)

    theme.make_button(frame, "+ Adicionar", lambda: OpenTeamWindow(self, frame, summaryFrame, categoryName, isDoublesPage),
                      variant="primary").pack(anchor="w", padx=10, pady=(5, 5))


  def UpdateTeamsSummary(self, frame:tk.Frame, categoryName:str, isDoublesPage:bool):
    ClearFrame(frame)
    summary = self.tournament.GetCategory(categoryName).GetTeamsSummary(not isDoublesPage)
    tk.Label(frame, text=summary, font=('Segoe UI', 16), bg=theme.BG, fg=theme.TEXT, justify="left").pack(anchor="w", padx=50, pady=90)


  def UpdateTeamsContent(self, teamsFrame:tk.Frame, summaryFrame:tk.Frame, categoryName:str, isDoublesPage=False):
    self.UpdateTeamsTables(teamsFrame, summaryFrame, categoryName, isDoublesPage)
    self.UpdateTeamsSummary(summaryFrame, categoryName, isDoublesPage)


  def UpdatePresentsAndAbsentsLists(self, categoryName, frame):

    def InsertPlayers(players, table:ttk.Treeview):
      for i, player in enumerate(players):
        if i % 2 == 0:
          tags = ('evenrow',)
        else:
          tags = ('oddrow',)
        table.insert(parent='', index='end', values=(player,), tags=tags)


    ClearFrame(frame)
    category = self.GetCategory(categoryName)

    presents = sorted([name for name, player in category.players.items() if player.isPresent])
    absents = sorted([name for name, player in category.players.items() if not player.isPresent])

    presentsTable = ttk.Treeview(frame, columns=("name"), show="headings", height=len(presents))
    presentsTable.heading("name", text="Presentes")
    presentsTable.tag_configure('oddrow', background=theme.SURFACE)
    presentsTable.tag_configure('evenrow', background=theme.ROW_ALT)
    presentsTable.pack(side="left", fill="both", expand=True, padx=(0,5))
    InsertPlayers(presents, presentsTable)

    absentsTable = ttk.Treeview(frame, columns=("name"), show="headings", height=len(absents))
    absentsTable.heading("name", text="Ausentes")
    absentsTable.tag_configure('oddrow', background=theme.SURFACE)
    absentsTable.tag_configure('evenrow', background=theme.ROW_ALT)
    absentsTable.pack(side="left", fill="both", expand=True, padx=(5,0))
    InsertPlayers(absents, absentsTable)

    def UpdatePresence(event:tk.Event):
      table:ttk.Treeview = event.widget
      for item in table.selection():
        playerName = table.item(item)["values"][0]
        player = category.GetPlayer(playerName)
        player.isPresent = not player.isPresent
      self.UpdatePresentsAndAbsentsLists(categoryName, frame)

    presentsTable.bind("<F5>", UpdatePresence)
    absentsTable.bind("<F5>", UpdatePresence)


  def UpdateOldDoublesContent(self):
    self.SetActiveNav("Duplas Antigas")
    self.SetTopbar("Duplas Antigas")
    self._section("Duplas de torneios anteriores")
    table = ttk.Treeview(self.contentFrame, columns=('player1', 'player2'), show="headings", height=len(self.tournament.oldDoubles))
    table.heading('player1', text="Jogador 1")
    table.heading('player2', text="Jogador 2")
    table.column('player1', width=250, anchor="w")
    table.column('player2', width=250, anchor="w")
    table.tag_configure('oddrow', background=theme.SURFACE)
    table.tag_configure('evenrow', background=theme.ROW_ALT)
    table.pack(anchor="w", padx=26, pady=10, fill="y", expand=True)

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
    category = self.GetCategory(categoryName)
    category.SortMatches()

    self.ClearContent()
    self.SetActiveNav("Jogos")
    self.SetTopbar("Jogos")

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

    if (category.categoryType == CategoryTypes.Groups and category.groups is not None) or (category.categoryType == CategoryTypes.SingleElimination):
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


  def UpdateGroupsContent(self, categoryName=None):
    category = self.GetCategory(categoryName)

    self.ClearContent()
    self.SetActiveNav("Grupos")
    self.SetTopbar("Grupos")

    combo = CreateCategoriesComboBox(self.contentFrame, self.tournament, categoryName)
    combo.bind("<<ComboboxSelected>>", lambda event: self.UpdateGroupsContent(event.widget.get()))

    if (category.groups is None) or (len(category.groups) == 0):
      tk.Label(self.contentFrame, text="Não há grupos nessa categoria.", font=('Segoe UI', 12), bg=theme.BG, fg=theme.TEXT_MUTED).pack(anchor="w", padx=26, pady=5)
      return

    for groupNumber in range(len(category.groups)):
      classification, isFinal = category.GetGroupClassification(groupNumber)
      isFinalText = 'finalizado' if isFinal else "em andamento"
      title = f"Grupo {groupNumber+1} ({isFinalText}):"
      CreateGroupClassificationTable(self, classification, title)


  def OpenNewTournamentWindow(self):
    OpenNewTournamentWindow(self)


  def OpenImportPlayersWindow(self):
    OpenImportPlayersWindow(self)


  def OpenExportTournamentWindow(self):
    OpenExportTournamentWindow(self)


  def StartCategory(self, category:Category):
    if category.isInitialized:
      messagebox.showwarning("Aviso", "Categoria já iniciada. Não é possível iniciá-la novamente.")
      return

    isConfirmed = messagebox.askyesno("Confirmação", f"Deseja realmente iniciar a categoria {category.name}?")
    if isConfirmed:
      try:
        self.tournament.StartCategory(category.name)
        self.UpdateCategories(category.name)
      except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao iniciar a categoria:\n\n{e}")


  def ExportPdf(self, category:Category):
    if not category.isInitialized:
      messagebox.showwarning("Aviso", "É preciso iniciar a categoria.")
      return

    filePath = filedialog.asksaveasfilename(
      title="Salvar arquivo como",
      initialfile=f"{self.tournament.name} - {category.name}.pdf",
      defaultextension=".pdf",
      filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
    )
    if filePath != '':
      ExportGroupCategoryToPdf(category, filePath)


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


  def _EmptyState(self, title, subtitle=""):
    self._hero(title, subtitle)


  def ShowContent(self, menuItem):
    self.ClearContent()

    if menuItem == "Torneio":
      self.UpdateTournamentContent()
      return

    if menuItem == "Categorias":
      categoryName = ""
      if self.tournament is not None and len(self.tournament.categories) > 0:
        categoryName = next(iter(self.tournament.categories))
      self.UpdateCategories(categoryName)
      return

    # demais telas exigem torneio + categorias
    self.SetActiveNav(menuItem)
    self.SetTopbar(menuItem)
    if self.tournament is None:
      self._EmptyState("Nenhum torneio carregado", "Crie ou abra um torneio para continuar.")
      return
    if menuItem != "Duplas Antigas" and len(self.tournament.categories) == 0:
      self._EmptyState("Nenhuma categoria criada", "Crie uma categoria primeiro.")
      return

    if (menuItem == "Jogadores") or (menuItem == "Duplas"):
      leftFrame = tk.Frame(self.contentFrame, bg=theme.BG)
      rightFrame = tk.Frame(self.contentFrame, bg=theme.BG)
      leftFrame.pack(side="left", fill="y", padx=16, pady=0)
      rightFrame.pack(side="left", fill="y", padx=0, pady=0)
      combobox = CreateCategoriesComboBox(leftFrame, self.tournament)
      isDoubles = menuItem == "Duplas"
      combobox.bind("<<ComboboxSelected>>", lambda event: self.UpdateTeamsContent(leftFrame, rightFrame, event.widget.get(), isDoubles))
      self.UpdateTeamsContent(leftFrame, rightFrame, combobox['values'][0], isDoubles)

    elif menuItem == "Presença":
      comboboxFrame = tk.Frame(self.contentFrame, bg=theme.BG)
      comboboxFrame.pack(fill="x", padx=16, pady=0)
      tablesFrame = tk.Frame(self.contentFrame, bg=theme.BG)
      tablesFrame.pack(fill="both", expand=True, padx=26, pady=16)
      combobox = CreateCategoriesComboBox(comboboxFrame, self.tournament)
      combobox.bind("<<ComboboxSelected>>", lambda event: self.UpdatePresentsAndAbsentsLists(event.widget.get(), tablesFrame))
      self.UpdatePresentsAndAbsentsLists(combobox['values'][0], tablesFrame)

    elif menuItem == "Duplas Antigas":
      self.UpdateOldDoublesContent()

    elif menuItem == "Jogos":
      self.UpdateMatchesContent()

    elif menuItem == "Grupos":
      self.UpdateGroupsContent()



if __name__ == "__main__":
  app = TournamentApp()
  app.mainloop()
