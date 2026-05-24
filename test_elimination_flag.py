"""Testes da flag 'tem fase eliminatória' por categoria.

Executar: python3 test_elimination_flag.py
"""
import os
import sys
import types
import tempfile

def _missing(name):
    try:
        __import__(name); return False
    except ImportError:
        return True

def _module(name):
    m = types.ModuleType(name); sys.modules[name] = m; return m

if _missing("pandas"):
    _module("pandas").DataFrame = type("DataFrame", (), {})
if _missing("oauth2client"):
    o = _module("oauth2client"); sa = _module("oauth2client.service_account")
    sa.ServiceAccountCredentials = type("SAC", (), {"from_json_keyfile_name": staticmethod(lambda *a, **k: None)})
    o.service_account = sa
if _missing("googleapiclient"):
    g = _module("googleapiclient"); d = _module("googleapiclient.discovery")
    d.build = lambda *a, **k: None; d.Resource = type("Resource", (), {}); g.discovery = d
if _missing("gspread"):
    gs = _module("gspread")
    gs.Client = type("Client", (), {}); gs.Spreadsheet = type("Spreadsheet", (), {})
    gs.authorize = lambda *a, **k: None
    u = _module("gspread.utils")
    u.rowcol_to_a1 = lambda r, c: f"R{r}C{c}"
    u.ValueInputOption = type("VIO", (), {"raw": type("r", (), {"value": "RAW"}), "user_entered": type("u", (), {"value": "U"})})
    gs.utils = u

from category import Category
from tournament import Tournament
from matchTeams import Player
from tennisEnums import CategoryTypes, MatchTypes
from fileReader import ReadInputFile
from fileSave import SaveFile
from GoogleSheets.tournamentExport import ExportEliminatoryStage

PASSED = []
def check(desc, got, expected):
    ok = got == expected; PASSED.append(ok)
    print(f"  [{'PASS' if ok else 'FALHOU'}] {desc}: obtido={got}, esperado={expected}")

def expect_raises(desc, fn):
    try:
        fn(); ok = False
    except Exception:
        ok = True
    PASSED.append(ok)
    print(f"  [{'PASS' if ok else 'FALHOU'}] {desc}: {'lançou' if ok else 'NÃO lançou'}")


class FakeConn:
    def __init__(self): self.written = []
    def AddWorkSheet(self, name): pass
    def WriteInWorkSheet(self, name, rng, values, isFormula=False): self.written.append(values)


def main():
    print("== Default por tipo ==")
    check("RoundRobin -> sem eliminatória", Category("a", CategoryTypes.RoundRobin).hasEliminationPhase, False)
    check("Groups -> com eliminatória", Category("a", CategoryTypes.Groups).hasEliminationPhase, True)
    check("SingleElimination -> com eliminatória", Category("a", CategoryTypes.SingleElimination).hasEliminationPhase, True)

    print("== Override explícito ==")
    check("RoundRobin forçado True", Category("a", CategoryTypes.RoundRobin, hasEliminationPhase=True).hasEliminationPhase, True)
    check("Groups forçado False", Category("a", CategoryTypes.Groups, hasEliminationPhase=False).hasEliminationPhase, False)

    print("== Persistência (round-trip) ==")
    t = Tournament("T", sets=1)
    t.AddCategory(Category("RR", CategoryTypes.RoundRobin, MatchTypes.Single))                     # False
    t.AddCategory(Category("SE", CategoryTypes.SingleElimination, MatchTypes.Single))              # True
    t.AddCategory(Category("RRx", CategoryTypes.RoundRobin, MatchTypes.Single, hasEliminationPhase=True))  # override
    for c in ("RR", "SE", "RRx"):
        t.AddTeam(Player("P1"), c); t.AddTeam(Player("P2"), c)
    fd, path = tempfile.mkstemp(suffix=".txt"); os.close(fd)
    try:
        SaveFile(path, t); r = ReadInputFile(path)
    finally:
        os.remove(path)
    check("RR persiste False", r.GetCategory("RR").hasEliminationPhase, False)
    check("SE persiste True", r.GetCategory("SE").hasEliminationPhase, True)
    check("RRx override persiste True", r.GetCategory("RRx").hasEliminationPhase, True)

    print("== Compatibilidade: arquivo antigo sem o campo -> default por tipo ==")
    fd, path = tempfile.mkstemp(suffix=".txt"); os.close(fd)
    try:
        with open(path, "w") as f:
            f.write("[TOURNAMENT]\nT,1,NormalSet,MatchTieBreak\n")
            f.write("[CATEGORIES]\nRR,RoundRobin,Single\nGR,Groups,Single\n[END]\n")
        old = ReadInputFile(path)
    finally:
        os.remove(path)
    check("antigo RoundRobin -> False", old.GetCategory("RR").hasEliminationPhase, False)
    check("antigo Groups -> True", old.GetCategory("GR").hasEliminationPhase, True)

    print("== Export: pula categorias sem eliminatória ==")
    t = Tournament("T", sets=1)
    t.AddCategory(Category("RR", CategoryTypes.RoundRobin, MatchTypes.Single))         # False -> pular
    t.AddCategory(Category("SE", CategoryTypes.SingleElimination, MatchTypes.Single))  # True
    conn = FakeConn()
    ExportEliminatoryStage(t, conn, {"SE": 4})
    flat = [cell for block in conn.written for row in block for cell in row]
    check("inclui categoria com eliminatória", "Categoria SE" in flat, True)
    check("pula round-robin", "Categoria RR" in flat, False)

    print("== Export: erro claro se faltar a fase de uma categoria marcada ==")
    t2 = Tournament("T", sets=1)
    t2.AddCategory(Category("SE", CategoryTypes.SingleElimination, MatchTypes.Single))
    expect_raises("fase ausente lança exceção", lambda: ExportEliminatoryStage(t2, FakeConn(), {}))

    print("\nRESULTADO:", "TODOS PASSARAM" if all(PASSED) else "HÁ FALHAS")
    raise SystemExit(0 if all(PASSED) else 1)


if __name__ == "__main__":
    main()
