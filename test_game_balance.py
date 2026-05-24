"""Testes do tiebreakão no saldo de games (configurável).

Executar: python3 test_game_balance.py
"""
import os
import sys
import types
import tempfile

# Stubs leves para as libs do Google (não precisam estar instaladas) ----------
def _missing(name):
    try:
        __import__(name)
        return False
    except ImportError:
        return True

def _module(name):
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m

if _missing("pandas"):
    _module("pandas").DataFrame = type("DataFrame", (), {})
if _missing("oauth2client"):
    o = _module("oauth2client")
    sa = _module("oauth2client.service_account")
    sa.ServiceAccountCredentials = type("SAC", (), {"from_json_keyfile_name": staticmethod(lambda *a, **k: None)})
    o.service_account = sa
if _missing("googleapiclient"):
    g = _module("googleapiclient")
    d = _module("googleapiclient.discovery")
    d.build = lambda *a, **k: None
    d.Resource = type("Resource", (), {})
    g.discovery = d
if _missing("gspread"):
    gs = _module("gspread")
    gs.Client = type("Client", (), {})
    gs.Spreadsheet = type("Spreadsheet", (), {})
    gs.authorize = lambda *a, **k: None
    u = _module("gspread.utils")
    u.rowcol_to_a1 = lambda r, c: f"R{r}C{c}"
    u.ValueInputOption = type("VIO", (), {"raw": type("r", (), {"value": "RAW"}), "user_entered": type("u", (), {"value": "U"})})
    gs.utils = u
# -----------------------------------------------------------------------------

import tennisHelper as tnh
from match import Match
from matchTeams import Player
from tennisEnums import SetTypes, ScoreTypes, MatchWinnerTypes
from tournament import Tournament
from category import Category
from tennisEnums import CategoryTypes, MatchTypes
from fileReader import ReadInputFile
from fileSave import SaveFile

PASSED = []
def check(desc, got, expected):
    ok = got == expected
    PASSED.append(ok)
    print(f"  [{'PASS' if ok else 'FALHOU'}] {desc}: obtido={got}, esperado={expected}")


def tiebreak_match(count):
    # GetMatchBalances é testado de forma isolada: define-se o resultado direto,
    # sem depender da validação de placar (que, sem o PR #1, rejeita o tiebreakão).
    m = Match(
        Player("A"), Player("B"),
        sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak,
        isTeam1Set=True, isTeam2Set=True, countTiebreakInGameBalance=count,
    )
    m.score = [(6, 4), (3, 6), (10, 8)]
    m.matchWinner = MatchWinnerTypes.Team1
    return m


def main():
    print("== GetMatchBalances: tiebreakão no saldo de games ==")
    # 6x4 3x6 10x8: sets A=2 B=1 -> setBalance +1 sempre.
    # com contar: games (6-4)+(3-6)+(10-8) = 1 ; sem contar: (6-4)+(3-6) = -1
    check("contando tiebreakão", tnh.GetMatchBalances(tiebreak_match(True)), (1, 1))
    check("sem contar tiebreakão", tnh.GetMatchBalances(tiebreak_match(False)), (1, -1))

    print("== Sets normais não são afetados pelo flag ==")
    m = Match(Player("A"), Player("B"), score=[(6, 4), (6, 3)], scoreType=ScoreTypes.Normal,
              sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak,
              isTeam1Set=True, isTeam2Set=True, countTiebreakInGameBalance=False)
    check("2x0 sem tiebreakão", tnh.GetMatchBalances(m), (2, 5))  # sets +2, games (6-4)+(6-3)=5

    print("== Flag propaga do torneio para os jogos ao iniciar categoria ==")
    for count in (True, False):
        t = Tournament("T", sets=1, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak,
                       countTiebreakInGameBalance=count)
        t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
        for i in range(3):
            t.AddTeam(Player(f"P{i}"), "A")
        t.StartCategory("A")
        anyMatch = next(iter(t.GetCategory("A").matches.values()))
        check(f"jogo herda flag={count}", anyMatch.countTiebreakInGameBalance, count)

    print("== Persistência (round-trip) do flag do torneio ==")
    t = Tournament("T", sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak,
                   countTiebreakInGameBalance=True)
    t.AddCategory(Category("A", CategoryTypes.RoundRobin, MatchTypes.Single))
    for i in range(3):
        t.AddTeam(Player(f"P{i}"), "A")
    fd, path = tempfile.mkstemp(suffix=".txt"); os.close(fd)
    try:
        SaveFile(path, t)
        reloaded = ReadInputFile(path)
    finally:
        os.remove(path)
    check("flag persiste como True", reloaded.countTiebreakInGameBalance, True)

    print("== Compatibilidade: arquivo antigo sem o campo -> False ==")
    # simula um [TOURNAMENT] sem o 5o campo
    fd, path = tempfile.mkstemp(suffix=".txt"); os.close(fd)
    try:
        with open(path, "w") as f:
            f.write("[TOURNAMENT]\nTorneio Velho,3,NormalSet,MatchTieBreak\n[END]\n")
        old = ReadInputFile(path)
    finally:
        os.remove(path)
    check("arquivo antigo -> não contar", old.countTiebreakInGameBalance, False)

    print("\nRESULTADO:", "TODOS PASSARAM" if all(PASSED) else "HÁ FALHAS")
    raise SystemExit(0 if all(PASSED) else 1)


if __name__ == "__main__":
    main()
