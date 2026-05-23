# Testes

Suíte de testes unitários (apenas `unittest`, da biblioteca padrão — não precisa
instalar nada).

## Como rodar

A partir da raiz do projeto:

```bash
python3 run_tests.py
# ou
python3 -m unittest discover -s tests -t .
```

Rodar um arquivo específico:

```bash
python3 -m unittest tests.test_tennis_helper -v
```

## O que é coberto

| Arquivo | Foco |
|---|---|
| `test_match_teams.py` | `Team` / `Player` / `Double` (seed, presença, nome de dupla) |
| `test_tennis_helper.py` | Validação de placar, seeding, byes, chaves, classificação, ordenação |
| `test_match.py` | `Match`: placar normal/inválido, W.O., desistência, bye, double bye, estado |
| `test_category.py` | `Category`: tipos, grupos, byes, primeira rodada, bracket, grupos→mata-mata, sorteio de duplas |
| `test_tournament.py` | `Tournament`: categorias, inscritos, iniciar categorias, brackets |
| `test_file_io.py` | `fileReader` / `fileSave`: parse, leitura de exemplo e round-trip |
| `test_google_sheets_export.py` | Helpers puros da exportação (nomes de fase, notação A1, ranges) |
| `test_pdf_exporter.py` | Geração de PDF de uma categoria (usa reportlab; pulado se ausente) |
| `test_imports.py` | Regressão do import circular `match` ↔ `tennisHelper` |

## Dependências externas

A lógica testada não exige as libs do Google Sheets nem o pandas. O pacote de
testes (`tests/__init__.py`) instala *stubs* leves para `gspread`, `pandas`,
`oauth2client` e `googleapiclient`, permitindo importar `tournament`,
`fileReader`, `fileSave` e o pacote `GoogleSheets` sem rede nem credenciais.

`reportlab` é usado de verdade quando instalado; se não estiver, os testes de PDF
são automaticamente pulados.
