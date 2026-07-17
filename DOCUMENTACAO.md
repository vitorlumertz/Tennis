# tzTennis — Gerenciador de Torneios de Tênis

Aplicação desktop (Python + tkinter) para **organizar e gerenciar torneios de tênis amador**:
inscrições, categorias, sorteio de chaves/grupos, lançamento de placares, classificação
automática, ranking entre etapas, exportação para PDF/HTML e integração com Google Sheets.

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
  classificados, com regras configuráveis por categoria (dois por grupo, um por grupo,
  dois nos grupos de 4 e um nos de 3, ou número total livre).
- **Calcula a classificação** dos grupos por vitórias, saldo de sets e saldo de games.
- **Consolida rankings** de várias etapas, com pontuação por fase, desempate e descarte do
  pior resultado.
- **Exporta** a categoria (grupos e jogos) para **PDF** e o torneio inteiro para o
  **Google Sheets** (com fórmulas que recalculam classificação e mata-mata sozinhas).
- **Exporta rankings para HTML**, em uma página responsiva e autocontida, pronta para
  publicação ou compartilhamento.
- **Salva/abre** o torneio em arquivo `.txt`.

---

## Estrutura do projeto

```
Tennis/
├── pyproject.toml       # Configuração do pacote Python e dependências de desenvolvimento
├── run_tests.py         # Atalho para executar a suíte de testes
├── tests.py             # Script de bancada/manual
│
├── src/
│   ├── tennis_manager/
│   │   ├── __init__.py
│   │   ├── tournament.py        # Classe Tournament — orquestra categorias e o fluxo do torneio
│   │   ├── category.py          # Classe Category — coração da lógica de chaveamento
│   │   ├── classification.py    # Critérios e cálculo de pontuação/classificação
│   │   ├── groupClassification.py # Montagem da chave eliminatória a partir dos classificados dos grupos
│   │   ├── match.py             # Classe Match — um jogo, seu placar e vencedor
│   │   ├── matchKey.py          # Classe MatchKey - guarda a informação da chave de um jogo
│   │   ├── matchTeams.py        # Team / Player / Double — os competidores
│   │   ├── ranking.py           # Consolida resultados de várias etapas em um ranking
│   │   ├── rankingHtmlExporter.py # Exporta o ranking para uma página HTML responsiva
│   │   ├── tennisEnums.py       # Enums: tipos de categoria, criação/classificação de grupos, set, placar, vencedor, seções de arquivo
│   │   ├── tennisExceptions.py  # Exceções de domínio (categoria/duplas/jogador duplicado etc.)
│   │   ├── tennisHelper.py      # Funções puras: validação de placar, seeding, byes, classificação
│   │   ├── fileReader.py        # Lê o arquivo .txt do torneio → objeto Tournament
│   │   ├── fileSave.py          # Salva o objeto Tournament → arquivo .txt
│   │   └── pdfExporter.py       # Exporta grupos/jogos de uma categoria para PDF (reportlab)
│   │
│   └── tennis_manager.egg-info/ # Metadados gerados pela instalação em modo editável
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
│   ├── updateGroupClassificationWindow.py # Diálogo "Atualizar Classificação dos Grupos"
│   ├── newTeamWindow.py        # Diálogo "Adicionar/Editar Jogador ou Dupla"
│   ├── changeCategoryWindow.py # Diálogo "Trocar de Categoria"
│   ├── matchesTable.py         # Tabela de jogos + janela de lançamento de placar
│   ├── classificationTables.py # Tabela de classificação de grupos
│   ├── classificationCriteriaSelector.py # Seletor de critérios de classificação
│   ├── resultPointsSelector.py # Seletor de pontuação por resultado
│   ├── playersImportWindow.py  # Diálogo de importação do Google Sheets
│   ├── updateClassificationCriteriaWindow.py # Diálogo "Atualizar Critérios de Classificação"
│   ├── updateResultPointsWindow.py # Diálogo "Atualizar Pontuação por Resultado"
│   └── exportTournamentWindow.py   # Diálogo de exportação para Google Sheets
│
├── tests/                     # Suíte de testes automatizados
│   ├── test_category.py
│   ├── test_classification.py
│   ├── test_file_io.py
│   ├── test_match.py
│   ├── test_tennis_helper.py
│   └── ...
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
      ├── groupDrawType / groupDrawQuantity  (regra de criação dos grupos)
      ├── groupClassificationType / numOfclassifiedsInGroups  (regra de classificação p/ mata-mata)
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
| `Groups`            | Fase de grupos configurável → classificados conforme `GroupClassificationTypes` → mata-mata. |
| `SingleElimination` | Eliminatória simples (chave de mata-mata desde o início). |
| `Automatic`         | Escolhe sozinho conforme o nº de inscritos (ver abaixo). |

**Regra do `Automatic`** (em `Category.UpdateCategoryType`):
- menos de 6 inscritos → `RoundRobin`
- de 6 a 9 → `Groups`
- 10 ou mais → `SingleElimination`

Além disso, uma categoria `Groups` com menos de 6 inscritos é rebaixada para `RoundRobin`.

### Criação da fase de grupos (`GroupDrawTypes`)

Categorias do tipo `Groups` têm duas propriedades persistidas no arquivo `.txt`:

- **`groupDrawType`** — define como a quantidade/tamanho dos grupos será calculada.
  O padrão é `ByGroupSize`.
- **`groupDrawQuantity`** — valor usado pelo tipo acima. O padrão é `3`.

| Tipo                 | Como usa `groupDrawQuantity` |
|----------------------|-------------------------------|
| `ByGroupSize`        | Interpreta o valor como tamanho mínimo de cada grupo. O valor deve ser ≥ 3. Ex.1: 14 inscritos com valor 4 → grupos de 4, 5 e 5. Ex.2: 14 inscritos com valor 5 → dois grupos de 7. Normalmente é usado com o valor igual a 3 para dividir os grupos em grupos de 3 e 4. |
| `ByNumberOfGroups`   | Interpreta o valor como quantidade total de grupos. Os inscritos são distribuídos de forma balanceada entre os grupos. A configuração é inválida se gerar algum grupo com menos de 3 participantes. Ex.: 10 inscritos em 3 grupos → grupos de 3, 3 e 4. |

Para preservar compatibilidade, arquivos antigos que não tenham esses campos são lidos como
`ByGroupSize` com `groupDrawQuantity = 3`, reproduzindo o comportamento clássico de grupos de
3 e 4.

### Classificação da fase de grupos (`GroupClassificationTypes`)

Propriedades da categoria (persistidas no arquivo `.txt`):

- **`groupClassificationType`** — regra de quantos times avançam do(s) grupo(s) para o mata-mata.
  Se omitido ao criar/ler, o padrão é `TwoPerGroup`.
- **`numOfclassifiedsInGroups`** — usado apenas quando o tipo é `TotalNumber`; indica o
  **número total** de classificados (deve ser ≥ nº de grupos).

| Tipo            | Comportamento |
|-----------------|---------------|
| `TwoPerGroup`   | Os 2 primeiros de **cada** grupo avançam (comportamento clássico). |
| `OnePerGroup`   | Apenas o 1º de cada grupo avança. |
| `TwoG4_OneG3`   | 2 classificados em grupos com 4 participantes e 1 classificado nos grupos 3. É necessário que todos os grupos possuam ou 3 ou 4 participantes. |
| `TotalNumber`   | N classificados no total, escolhidos entre os melhores colocados de todos os grupos (`numOfclassifiedsInGroups`). |

O nº de vagas na chave eliminatória é calculado em `Category.__GetNumberOfClassifiedsInGroups()`
e usado em `GetBracket` e em `UpdateBracket` (via `groupClassification.GetTeams` /
`GetBracketWithTeams`) para montar o mata-mata respeitando cabeças de chave por grupo e
evitando reencontros precoce entre integrantes do mesmo grupo.

### Tipos de set (`SetTypes`)

`NormalSet` (vai a 6 games), `ShortSet` (4), `LongSet` (8), `MatchTieBreak` (10) e
`NotDefined`. Um torneio define o nº de sets (1, 3 ou 5), o tipo de set e o tipo do
**último** set (tipicamente um match tie-break no set decisivo).

### Tipos de placar (`ScoreTypes`)

`Normal`, `WO_to_T1`/`WO_to_T2` (W.O. para o time 1/2), `DoubleWO`, `T1Forfeit`/`T2Forfeit`
(desistência), `Bye_to_T1`/`Bye_to_T2` (bye), `DoubleBye`, `NotDefined`, `Invalid`.

---

## Lógica de chaveamento (o "cérebro", em `category.py` + `tennisHelper.py`)

### Chaves dos jogos (MatchKey)

Cada jogo tem uma chave-string de 8 caracteres que codifica fase + tipo + número, o que
permite ordenar e navegar a chave:

- `001SE001` — **S**ingle **E**limination (mata-mata). Os 3 primeiros dígitos são o "stage"
  (jogos restantes naquela fase): `001`=Final, `002`=Semifinais, `004`=Quartas,
  `008`=Oitavas, `016`=R32. Os 3 últimos são o número do jogo dentro da fase.
- `001GR001` — jogo da fase de **GR**upos (1º grupo, jogo 1).
- `006RR001` — jogo de grupo único (**R**ound-**R**obin); o prefixo guarda o total de jogos.

`MatchKey.NextKey()` calcula, a partir da chave de um jogo eliminatório, qual é o próximo
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
- **Groups**: monta os grupos conforme `groupDrawType` / `groupDrawQuantity`
  (`GetNumberOfGroups`), distribui 1 seed por grupo e espalha os demais, depois cria os jogos
  de cada grupo.

### Montagem e avanço da chave (`GetBracket`, `CompleteMatches`, `UpdateBracket`)

- `GetBracket` cria o **mapa de avanço** (`bracket`): cada jogo → próximo jogo, até a final
  (`001SE001 → None`).
- `CompleteMatches` cria os jogos "vazios" das fases futuras.
- `UpdateBracket` é chamada a cada placar lançado:
  - promove o vencedor de cada jogo eliminatório para o jogo seguinte;
  - quando a fase de grupos termina (todos os jogos definidos), calcula os classificados
    conforme `groupClassificationType` / `numOfclassifiedsInGroups` e **monta automaticamente
    o mata-mata** entre eles (`groupClassification.py`: 1ºs como cabeças, demais posições
    sorteadas nos lados opostos da chave para evitar reencontro precoce).

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

Seções (`FileSections`): `[TOURNAMENT]`, `[CATEGORIES]`,
`[PLAYERS]`, `[OLDDOUBLES]`, `[DOUBLES]`, `[GROUPS]`, `[MATCHES]`, `[END]`.

Exemplo (de `TestData/`):

```
[TOURNAMENT]
//Name, Number of Sets, Set Type, Last Set Type
Torneio Exemplo,1,Normal Set,MatchTieBreak

[CATEGORIES]
//Name, Category Type, Match Type, Is Groups Finished, Random Doubles, Initialized, Group Classification Type, Num Of Classifieds In Groups, Group Draw Type, Group Draw Quantity
1a Classe Simples,SingleElimination,Single
2a Classe Simples,Groups,Single,,,True,TwoPerGroup,,ByGroupSize,3
3a Classe Simples,Groups,Single,,,True,TotalNumber,8,ByNumberOfGroups,4

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

## Ranking entre etapas (`ranking.py`)

`Ranking(name, tournaments, ...)` agrega uma sequência ordenada de objetos `Tournament`.
Cada torneio corresponde a uma etapa e cria uma coluna numérica (`"1"`, `"2"`, ...). Novas
etapas também podem ser incluídas com `AddTournament(tournament)`; nomes de torneio repetidos
são rejeitados.

A tabela `Ranking.data` é um `pandas.DataFrame` com categoria, posição, nome, total de pontos,
valor descartado e pontuação por etapa. As posições são calculadas separadamente por categoria.

### Pontuação padrão

- **Mata-mata:** campeão 10, finalista 8, semifinalista 6 e derrotados nas fases anteriores
  recebem 4, 3, 2 ou 1 ponto conforme a fase (`4`, `8`, `16` ou `32`). Fases sem valor
  configurado geram erro.
- **Round-robin:** os quatro primeiros recebem, respectivamente, 10, 8, 6 e 4 pontos, exceto
  o último colocado; os demais resultados recebem o número de vitórias mais 1.
- **Fase de grupos:** cada participante começa com 1 ponto e soma 1 por vitória; quem também
  disputa o mata-mata passa a receber a pontuação correspondente à fase alcançada.

Os mapas podem ser substituídos por `defaultEliminatoryPoints` e
`defaultRoundRobinPoints`. Em categorias de duplas, `isIndividual=True` (padrão) atribui os
mesmos pontos a cada jogador da parceria; com `isIndividual=False`, a dupla permanece como
uma única entrada.

Por padrão, `discardWorstValue=True` subtrai a menor pontuação de quem participou de todas as
etapas adicionadas. Quem não disputou alguma etapa não tem descarte. O desempate considera,
depois do total, a quantidade de resultados com a maior pontuação existente, depois com a
segunda maior, e assim sucessivamente. Se todos esses critérios forem iguais, a posição é
compartilhada e a numeração seguinte mantém a lacuna (por exemplo: 1, 1, 3).

Exemplo de uso:

```python
from tennis_manager.fileReader import ReadInputFile
from tennis_manager.ranking import Ranking
from tennis_manager.rankingHtmlExporter import ExportToHtml

etapas = [
    ReadInputFile("etapa-1.txt"),
    ReadInputFile("etapa-2.txt"),
]
ranking = Ranking("Ranking 2026", etapas, isIndividual=True)
ExportToHtml(ranking, "ranking-2026.html")
```

O ranking não é persistido no formato `.txt`; ele é sempre calculado em memória a partir
dos torneios carregados no momento da requisição.

---

## Exportação do ranking para HTML (`rankingHtmlExporter.py`)

`ExportToHtml(ranking, filePath)` grava em UTF-8 uma página completa e autocontida, sem
JavaScript nem arquivos externos. O documento contém:

- uma tabela por categoria, com posição, nome, total, pontos de cada etapa e descarte;
- apenas o top 5 inicialmente, com controle para exibir a classificação completa quando
  houver mais colocados;
- colunas de posição e nome fixas durante a rolagem horizontal, além de adaptação para telas
  estreitas;
- gráfico de inscritos por etapa, empilhado por categoria, com totais, legenda e detalhes em
  cada segmento.

Nomes do ranking, categorias, participantes e títulos exibidos são escapados antes de entrar
no HTML. A exportação existe na API Python e ainda não possui comando próprio na interface
tkinter.

---

## Interface gráfica (`Interface/`)

App tkinter de janela única (`TournamentApp`, abre maximizada) com **menu lateral** e área de
conteúdo rolável. Itens do menu:

| Menu            | O que faz |
|-----------------|-----------|
| **Torneio**     | Mostra dados do torneio; botões: criar, abrir, importar do Sheets, exportar p/ Sheets. |
| **Categorias**  | Detalhes da categoria (incl. criação dos grupos, tipo de classificação dos grupos e nº de classificados); iniciar categoria, exportar PDF, criar, atualizar classificação dos grupos e excluir categoria. |
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

- A classe `Ranking` funciona em memória, é recalculada a partir dos torneios e não é
  persistida nos arquivos `.txt`; a exportação HTML ainda não está exposta na interface tkinter.
- Não há launcher para a interface; sua execução ainda depende da configuração manual do
  `PYTHONPATH`. O projeto possui testes automatizados com `unittest` e empacotamento via
  `pyproject.toml`.
- Persistência apenas em arquivo `.txt` (sem banco de dados).
