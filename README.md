# Tennis Manager

A Python package for building and managing tennis tournaments. `tennis_manager` provides
the domain model and rules needed to register participants, generate groups and knockout
brackets, track scores, calculate standings, persist tournament data, and export results.

The repository also includes a Tkinter desktop application that provides a graphical
interface for the package.

## Purpose

The main purpose of this repository is to develop the reusable `tennis_manager` package. It
centralizes the tournament domain model and competition rules so they can be used from Python
applications, scripts, automated workflows, or any other interface.

The included desktop application is one available interface and an example of how the package
can support a complete tournament management workflow.

## Key Features

- singles and doubles tournaments;
- round-robin, group-stage, and single-elimination categories;
- seed and bye placement;
- doubles draws with control over previous pairings;
- score validation and support for walkovers, forfeits, and byes;
- standings based on wins, set difference, and game difference;
- automatic winner advancement through the bracket;
- tournament persistence in text files;
- PDF generation and HTML ranking export;
- optional Google Sheets import and export;
- a Tkinter desktop interface included as a separate application layer.

## Requirements

- Python 3.10 or newer;
- `pip`.

The package dependencies are declared in `pyproject.toml` and installed automatically by
`pip`. Tkinter is only required for the optional desktop interface.

## Installation

Clone the repository, open its directory, and create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

To also enable the Google Sheets integration:

```bash
python -m pip install -e ".[google]"
```

## Package Usage

After installation, import the package directly into a Python application or script. This
example reads a saved tournament and lists its categories:

```python
from tennis_manager.fileReader import ReadInputFile

tournament = ReadInputFile("TestData/TournamentExample1.txt")

print(tournament.name)
for category in tournament.categories.values():
    print(category.name, len(category.teams))
```

The package includes modules for tournaments, categories, players and doubles teams, matches,
standings, rankings, persistence, and PDF/HTML export. See
[`DOCUMENTACAO.md`](DOCUMENTACAO.md) for the complete domain model and API details.

## Desktop Interface

The repository includes an optional Tkinter application for managing tournaments through a
graphical interface. From the repository root, start it with:

```bash
python Interface/tournamentApp.py
```

Tkinter is included with most Python installations. On Ubuntu and derived distributions, it
can be installed with:

```bash
sudo apt install python3-tk
```

A typical workflow is:

1. create a tournament;
2. add one or more categories;
3. register players or doubles teams;
4. start the categories to generate groups and brackets;
5. enter match results;
6. save the tournament or export its data.

You can also open one of the files under `TestData/` to explore an example tournament.

## Tournament File Example

The package uses a text-based persistence format divided into sections. A minimal file starts
as follows:

```text
[TOURNAMENT]
//Name, Number of Sets, Set Type, Last Set Type
Example Tournament,1,Normal Set,MatchTieBreak

[CATEGORIES]
//Name, Category Type, Match Type, Is Groups Finished, Random Doubles, Initialized
Open Category,SingleElimination,Single,False,False,False

[PLAYERS]
//Name, Category Name, Seed Number
Player A,Open Category,1
Player B,Open Category,2
```

See the complete files under [`TestData/`](TestData/) and the detailed format description in
[`DOCUMENTACAO.md`](DOCUMENTACAO.md).

## Google Sheets Integration

The integration uses a Google service account. After installing the optional dependencies,
place its credentials file at `credential.json` in the directory from which the application
is run. Share the target spreadsheet or folder with the service account email address.

> **Security:** never commit `credential.json` to the repository. The file is already
> included in `.gitignore`, but any credentials that have been exposed should be revoked and
> replaced.

## Tests

Run the complete test suite from the repository root:

```bash
python run_tests.py
```

Alternatively:

```bash
python -m unittest discover -s tests -t .
```

To run a single test module:

```bash
python -m unittest tests.test_tennis_helper -v
```

## Project Structure

```text
Tennis/
├── src/tennis_manager/  # main package: domain rules, persistence, and exporters
├── Interface/           # optional Tkinter graphical interface
├── GoogleSheets/        # spreadsheet import and export
├── TestData/            # example tournaments
├── tests/               # automated tests
├── DOCUMENTACAO.md      # detailed technical documentation
├── pyproject.toml       # package metadata and dependencies
└── run_tests.py         # test suite runner
```

## Documentation

The technical documentation describes the domain model, category formats, group rules,
standings, bracket generation, rankings, exporters, and persistence format:

- [`DOCUMENTACAO.md`](DOCUMENTACAO.md)
- [`tests/README.md`](tests/README.md)

## Contributing

Contributions are welcome. Before submitting a change:

1. create a dedicated branch;
2. keep the change focused and add tests when applicable;
3. run the complete test suite;
4. clearly describe the problem being solved and any behavior changes.
