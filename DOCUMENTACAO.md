# LumertzTennis — Gerenciador de Torneios de Tênis

Aplicação desktop (Python + tkinter) para **organizar e gerenciar torneios de tênis amador**:
inscrições, categorias, sorteio de chaves/grupos, lançamento de placares, classificação
automática, exportação para PDF e integração com Google Sheets.

O título da janela é "Gerenciador de Torneios de Tênis". Todo o estado de um torneio vive em
memória e é persistido em um **arquivo de texto `.txt`** próprio (formato descrito abaixo).

---

## O que o sistema faz (resumo)

- **Cria torneios** definindo nº de sets, tipo de set e tipo do set decisivo.
- **Organiza categorias** (ex.: "1ª Classe Simples", "Duplas A"), cada uma com seu próprio
  formato de disputa: pode ser simples ou duplas.
- **Gerencia inscritos** (jogadores ou duplas), com número de cabeça de chave.
- **Importa inscritos** automaticamente de uma planilha do **Google Sheets**.
- **Controla presença** dos jogadores no dia do torneio.
- **Sorteia duplas** aleatoriamente respeitando o equilíbrio por cabeça de chave e evitando
  repetir duplas de torneios anteriores ("duplas antigas").
- **Gera as chaves automaticamente** conforme o formato da categoria:
  round-robin (todos contra todos), fase de grupos + mata-mata, ou eliminatória simples —
  posicionando cabeças de chave e byes nas posições corretas.
- **Lança placares**, valida o resultado (set/games coerentes) e trata casos especiais
  (WO, desistência, bye).
- **Avança a chave** automaticamente: ao registrar o vencedor de um jogo, ele é promovido
  para o jogo seguinte; ao fechar a fase de grupos, monta a chave eliminatória entre os
  classificados.
- **Calcula a classificação** dos grupos por vitórias, saldo de sets e saldo de games.
- **Exporta** a categoria (grupos e jogos) para **PDF** e o torneio inteiro para o
  **Google Sheets** (com fórmulas que recalculam classificação e mata-mata sozinhas).
- **Salva/abre** o torneio em arquivo `.txt`.

---

## Estrutura do projeto

```
LumertzTennis/
├── tournament.py        # Classe Tournament — orquestra categorias e o fluxo do torneio
├── category.py          # Classe Category — coração da lógica de chaveamento (511 linhas)
├── match.py             # Classe Match — um jogo, seu placar e vencedor
├── matchTeams.py        # Team / Player / Double — os competidores
├── ranking.py           # Classe Ranking — esqueleto (não implementado ainda)
├── tennisEnums.py       # Enums: tipos de categoria, set, placar, vencedor, seções de arquivo
├── tennisExceptions.py  # Exceções de domínio (categoria/duplas/jogador duplicado etc.)
├── tennisHelper.py      # Funções puras: validação de placar, seeding, byes, classificação
├── fileReader.py        # Lê o arquivo .txt do torneio → objeto Tournament
├── fileSave.py          # Salva o objeto Tournament → arquivo .txt
├── pdfExporter.py       # Exporta grupos/jogos de uma categoria para PDF (reportlab)
├── tests.py             # Script de bancada (não é suíte de testes automatizada)
│
├── GoogleSheets/
│   ├── googleSheetsUtils.py   # Conexão com Sheets/Drive (gspread + google-api)
│   ├── playersImport.py       # Importa inscritos da planilha
│   └── tournamentExport.py    # Exporta grupos + mata-mata com fórmulas
│
├── Interface/                 # Camada de UI (tkinter) — uma janela/tela por arquivo
│   ├── tournamentApp.py       # Janela principal, menu lateral, roteamento de telas
│   ├── interfaceUtils.py      # Helpers de UI (combobox de categorias, limpar frame)
│   ├── newTournamentWindow.py # Diálogo "Novo Torneio"
│   ├── newCategoryWindow.py   # Diálogo "Nova Categoria"
│   ├── newTeamWindow.py       # Diálogo "Adicionar/Editar Jogador ou Dupla"
│   ├── changeCategoryWindow.py# Diálogo "Trocar de Categoria"
│   ├── matchesTable.py        # Tabela de jogos + janela de lançamento de placar
│   ├── classificationTables.py# Tabela de classificação de grupos
│   ├── playersImportWindow.py # Diálogo de importação do Google Sheets
│   └── exportTournamentWindow.py # Diálogo de exportação para Google Sheets
│
└── TestData/                  # Torneios de exemplo (entradas e saídas) p/ testes manuais
```

---

## Conceitos do domínio

### Hierarquia

```
Tournament  (o torneio)
 └── Category  (categoria; várias por torneio)
      ├── teams / players  (inscritos: Player ou Double)
      ├── groups           (grupos, quando aplicável)
      ├── matches          (todos os jogos, indexados por "chave de jogo")
      └── bracket          (mapa de avanço: cada jogo aponta para o próximo)
```

### Competidores (`matchTeams.py`)

- **`Team`** — base. Tem `name`, `seedNumber` (nº de cabeça de chave; 0 = sem seed) e
  `isSeed`.
- **`Player(Team)`** — jogador individual; acrescenta `isPresent` (presença no dia).
- **`Double(Team)`** — dupla de dois `Player`; o nome é `"Jogador1/Jogador2"`.

### Tipos de categoria (`CategoryTypes`)

| Tipo                | Comportamento |
|---------------------|---------------|
| `RoundRobin`        | Todos contra todos (grupo único). Usado para poucos inscritos. |
| `Groups`            | Fase de grupos (de 3 e 4) → classificam os 2 primeiros de cada grupo → mata-mata. |
| `SingleElimination` | Eliminatória simples (chave de mata-mata desde o início). |
| `Automatic`         | Escolhe sozinho conforme o nº de inscritos (ver abaixo). |
| `DoubleElimination`, `Teams` | Declarados no enum, **não implementados**. |

**Regra do `Automatic`** (em `Category.UpdateCategoryType`):
- menos de 6 inscritos → `RoundRobin`
- de 6 a 9 → `Groups`
- 10 ou mais → `SingleElimination`

Além disso, uma categoria `Groups` com menos de 6 inscritos é rebaixada para `RoundRobin`.

### Tipos de set (`SetTypes`)

`NormalSet` (vai a 6 games), `ShortSet` (4), `LongSet` (8), `MatchTieBreak` (10) e
`NotDefined`. Um torneio define o nº de sets (1, 3 ou 5), o tipo de set e o tipo do
**último** set (tipicamente um match tie-break no set decisivo).

### Tipos de placar (`ScoreTypes`)

`Normal`, `WO_to_T1`/`WO_to_T2` (W.O. para o time 1/2), `DoubleWO`, `T1Forfeit`/`T2Forfeit`
(desistência), `Bye_to_T1`/`Bye_to_T2` (bye), `DoubleBye`, `NotDefined`, `Invalid`.

---

## Lógica de chaveamento (o "cérebro", em `category.py` + `tennisHelper.py`)

### Chaves dos jogos (match keys)

Cada jogo tem uma chave-string de 8 caracteres que codifica fase + tipo + número, o que
permite ordenar e navegar a chave:

- `001FP001` — **F**ase **P**rincipal (mata-mata). Os 3 primeiros dígitos são o "stage"
  (jogos restantes naquela fase): `001`=Final, `002`=Semifinais, `004`=Quartas,
  `008`=Oitavas, `016`=R32. Os 3 últimos são o número do jogo dentro da fase.
- `001GR001` — jogo da fase de **GR**upos (1º grupo, jogo 1).
- `006GU001` — jogo de **G**rupo **Ú**nico (round-robin); o prefixo guarda o total de jogos.

`GetNextMatchKey()` calcula, a partir da chave de um jogo eliminatório, qual é o próximo
jogo e se o vencedor entra como time 1 ou time 2 — é isso que faz a chave "subir".

### Cabeças de chave e posicionamento (seeding)

`GetSeedsPositions(numPlayers, numSeeds)` gera o espalhamento padrão de seeds numa chave de
potência de 2 (1 vs 2 na final teórica, 1/4/3/2 nas semis, etc.). `GetSeeds()` escolhe quem
são as cabeças: respeita os `seedNumber` informados e, se faltarem, **sorteia** seeds entre
os não-cabeças; se sobrarem, rebaixa os excedentes.

### Byes

Quando o nº de inscritos não é potência de 2, faltam vagas que viram **byes**.
`GetNumberOfByes()` calcula quantos (até a próxima potência de 2) e `GetByes()` distribui:
os byes vão **primeiro para as cabeças de chave** (que avançam direto), e o restante para
não-cabeças.

### Geração da primeira rodada (`GetFirstRound`)

- **RoundRobin**: cria todos os confrontos possíveis (`itertools.combinations`).
- **SingleElimination**: posiciona seeds, distribui byes e preenche o resto com não-cabeças
  sorteados.
- **Groups**: monta grupos de 3 e 4 (`GetNumberOfGroups`: `n % 3` grupos de 4, o resto de 3),
  distribui 1 seed por grupo e espalha os demais, depois cria os jogos de cada grupo.

### Montagem e avanço da chave (`GetBracket`, `CompleteMatches`, `UpdateBracket`)

- `GetBracket` cria o **mapa de avanço** (`bracket`): cada jogo → próximo jogo, até a final
  (`001FP001 → None`).
- `CompleteMatches` cria os jogos "vazios" das fases futuras.
- `UpdateBracket` é chamada a cada placar lançado:
  - promove o vencedor de cada jogo eliminatório para o jogo seguinte;
  - quando a fase de grupos termina (todos os jogos definidos), calcula os classificados e
    **monta automaticamente o mata-mata** entre eles (1ºs como cabeças, 2ºs sorteados nos
    lados opostos da chave para evitar reencontro precoce).

### Classificação dos grupos (`tennisHelper.GetClassification`)

Critérios de desempate, nesta ordem:
1. **Vitórias**
2. **Saldo de sets**
3. **Saldo de games**

### Sorteio de duplas (`Category.DrawDubles`)

Para categorias de duplas com `isRandomDoubles`:
- agrupa jogadores por `seedNumber` e os emparelha pela **soma de seeds** (o melhor com o
  pior, e assim por diante), equilibrando as duplas;
- evita formar duplas que já existiram (lista de **"duplas antigas"** do torneio);
- tenta até 1000 vezes; se não conseguir um sorteio válido, lança `DrawingDoublesError`.

### Validação de placar (`tennisHelper.IsValidScore` / `IsValidSetScore`)

Confere que: o nº de sets é ímpar, cada set tem um placar coerente com o tipo de set
(ex.: NormalSet aceita 6x0..6x4, 7x5, 7x6; MatchTieBreak vai a 10 com diferença de 2), e
que um dos lados venceu a maioria dos sets. Retorna quem venceu ou `NotDefined` (placar
inválido).

---

## Formato do arquivo de torneio (`.txt`)

O torneio é salvo/lido como texto dividido em **seções** entre colchetes. Linhas que começam
com `//` são comentários (cabeçalhos de coluna) e linhas em branco são ignoradas. Os campos
são separados por vírgula.

Seções (`FileSections`): `[RANKING]` (reservado), `[TOURNAMENT]`, `[CATEGORIES]`,
`[PLAYERS]`, `[OLDDOUBLES]`, `[DOUBLES]`, `[GROUPS]`, `[MATCHES]`, `[END]`.

Exemplo (de `TestData/`):

```
[TOURNAMENT]
//Name, Number of Sets, Set Type, Last Set Type
Torneio Exemplo,1,Normal Set,MatchTieBreak

[CATEGORIES]
//Name, Category Type, Match Type, Is Groups Finished, Random Doubles, Initialized
1a Classe Simples,SingleElimination,Single
2a Classe Simples,Groups,Single

[PLAYERS]
//Name, Category Name, Seed Number
Player A,1a Classe Simples,1
Player B,1a Classe Simples,2

[GROUPS]
//Category, Group, Player
2a Classe Simples,1,PlayerA

[MATCHES]
//Category, Key, Player 1, Player 2, Score, Score Type, Sets, Set Type, ...
```

- `fileReader.ReadInputFile(path)` → reconstrói o objeto `Tournament`.
- `fileSave.SaveFile(path, tournament)` → grava o estado completo.

`credential.json` (chave de service account do Google) e `__pycache__/` estão no `.gitignore`.

---

## Integração com Google Sheets (`GoogleSheets/`)

Autenticação via **service account** (`credential.json` na pasta de execução), usando
`gspread` + `google-api-python-client` (`googleSheetsUtils.GoogleSheetsConnection`).

- **Importar inscritos** (`playersImport.GetPlayersFromSheet`): lê uma planilha (por título +
  ID da pasta do Drive + nº da guia) com as colunas `Category` e `Player`, e adiciona cada
  jogador à categoria correspondente. Linhas sem jogador são ignoradas; falhas (ex.: categoria
  inexistente) são reportadas na UI.
- **Exportar torneio** (`tournamentExport.ExportTournamentToGoogleSheets`): cria abas com a
  **fase de grupos** e a **fase eliminatória**, preenchidas com **fórmulas do Google Sheets em
  português** (`SE`, `SOMASE`, `ORDEM`, `CONT.SES`, `E`, `FALSO`). Assim, ao digitar os games
  na planilha, a classificação dos grupos e o avanço do mata-mata se recalculam sozinhos.
  A exportação recebe, por categoria, a fase em que o mata-mata começa (ex.: `{"A":8,"B":4}`).

---

## Exportação para PDF (`pdfExporter.py`)

`ExportGroupCategoryToPdf(category, path)` gera, com **reportlab**, um PDF (A4) listando os
grupos (ou o grupo único, em round-robin), seus integrantes e os jogos de cada grupo —
quebrando páginas automaticamente. Útil para imprimir as chaves no dia do torneio.

---

## Interface gráfica (`Interface/`)

App tkinter de janela única (`TournamentApp`, abre maximizada) com **menu lateral** e área de
conteúdo rolável. Itens do menu:

| Menu            | O que faz |
|-----------------|-----------|
| **Torneio**     | Mostra dados do torneio; botões: criar, abrir, importar do Sheets, exportar p/ Sheets. |
| **Categorias**  | Detalhes da categoria; iniciar categoria, exportar PDF, criar e excluir categoria. |
| **Jogadores**   | Tabela de jogadores + resumo (contagem por cabeça de chave). |
| **Presença**    | Listas de presentes/ausentes. |
| **Duplas**      | Tabela de duplas da categoria. |
| **Duplas Antigas** | Duplas de torneios anteriores (para o sorteio evitar repetições). |
| **Jogos**       | Tabela de jogos por fase/grupo; lançamento de placar. |
| **Grupos**      | Classificação ao vivo de cada grupo (finalizado/em andamento). |
| **Salvar Torneio** | Salva em `.txt`. |

**Atalhos de teclado** (nas tabelas):
- `Delete` — excluir item(ns) selecionado(s)
- `F2` — editar jogador/dupla **ou** lançar placar de um jogo
- `F3` — trocar os números de cabeça de chave entre dois itens
- `F4` — mover item(ns) para outra categoria
- `F5` — alternar presença (presente/ausente)

"Iniciar categoria" dispara `Tournament.StartCategory`: sorteia duplas (se for o caso), gera a
primeira rodada, monta a chave e cria os jogos — depois disso a categoria fica `isInitialized`
e não pode ser reiniciada.

---

## Como executar

### Requisitos

- **Python 3** (usa type hints modernos como `dict[str,Category]`, `X|None` → recomendado 3.10+).
- **tkinter** (vem com o Python na maioria das distros; no Ubuntu: `sudo apt install python3-tk`).
- Bibliotecas Python:
  ```
  pip install reportlab gspread oauth2client google-api-python-client pandas
  ```
- Para a integração com Sheets: um arquivo **`credential.json`** (service account do Google,
  com acesso ao Drive/Sheets) na pasta a partir da qual o app é executado.

### Rodando o app

O ponto de entrada é `Interface/tournamentApp.py`. Os módulos da raiz e os de `Interface/`
são importados como top-level (ex.: `from tennisEnums import ...` e
`from interfaceUtils import ...`), então **a raiz do projeto e a pasta `Interface/` precisam
estar no `PYTHONPATH`**. Exemplo, a partir da raiz do projeto:

```bash
PYTHONPATH=.:Interface python Interface/tournamentApp.py
```

> Observação: o `tests.py` usa caminhos no estilo Windows (`.\TestData\...`); o projeto foi
> desenvolvido em ambiente Windows. Em Linux, ajuste os caminhos se for rodá-lo.

### `tests.py`

Não é uma suíte automatizada — é um **script de bancada** para carregar um torneio de exemplo
de `TestData/`, e (linhas comentáveis) iniciar categorias, imprimir chaves/jogos, salvar ou
exportar para o Sheets.

---

## Estado atual e limitações

- `RANKING` e a classe `Ranking` são **esqueletos** (sem implementação): a ideia é agregar
  vários torneios num ranking, mas ainda não foi feito.
- `CategoryTypes.DoubleElimination` e `CategoryTypes.Teams` estão no enum mas **não são
  tratados** na lógica de chaveamento.
- Não há testes automatizados nem README/empacotamento; a execução depende de configurar o
  `PYTHONPATH` manualmente (não há `__init__.py`/launcher).
- Persistência apenas em arquivo `.txt` (sem banco de dados).
- Existem comentários/observações no código apontando possíveis ajustes (ex.: em
  `GetMatchBalances`, dúvida sobre pontos de tie-break entrarem no saldo de games).
