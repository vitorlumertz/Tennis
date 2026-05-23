"""Testes de validação de placar (stdlib, sem dependências externas).

Executar: python3 test_score_validation.py
"""
import tennisHelper as tnh  # importar primeiro evita o import circular com match
from match import Match
from matchTeams import Player
from tennisEnums import SetTypes, ScoreTypes, MatchWinnerTypes


def check(desc, got, expected):
    status = "PASS" if got == expected else "FALHOU"
    print(f"  [{status}] {desc}: obtido={got}, esperado={expected}")
    return got == expected


def main():
    ok = True

    # Set decisivo em match tie-break (config padrão: sets=3, lastSetType=MatchTieBreak)
    ok &= check(
        "3 sets com tie-break decisivo 10x8 é válido",
        tnh.IsValidScore([(6, 4), (3, 6), (10, 8)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
        MatchWinnerTypes.Team1,
    )

    # Categoria de short set: 4x1 4x2 deve ser válido
    ok &= check(
        "short set 4x1 4x2 é válido",
        tnh.IsValidScore([(4, 1), (4, 2)], 3, SetTypes.ShortSet, SetTypes.ShortSet),
        MatchWinnerTypes.Team1,
    )

    # Regressão: sets=1 com lastSetType=MatchTieBreak NÃO deve aplicar o tie-break
    # ao único set (os dados de exemplo usam essa config com placares de set normal).
    ok &= check(
        "sets=1 valida o único set como setType (6x0 válido)",
        tnh.IsValidScore([(6, 0)], 1, SetTypes.NormalSet, SetTypes.MatchTieBreak),
        MatchWinnerTypes.Team1,
    )

    # Vitória em sets diretos (best of 3) usa setType, não lastSetType
    ok &= check(
        "best of 3 vencido em 2x0 usa setType",
        tnh.IsValidScore([(6, 4), (6, 3)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
        MatchWinnerTypes.Team1,
    )

    # Caminho real: Match.SetScore deve marcar Normal/Team1, não Invalid
    m = Match(
        Player("A"), Player("B"),
        score=[(6, 4), (3, 6), (10, 8)], scoreType=ScoreTypes.Normal,
        sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak,
    )
    ok &= check("Match.SetScore com tie-break decisivo -> scoreType", m.scoreType, ScoreTypes.Normal)
    ok &= check("Match.SetScore com tie-break decisivo -> vencedor", m.matchWinner, MatchWinnerTypes.Team1)

    # Placar inválido continua inválido
    ok &= check(
        "placar incoerente continua inválido",
        tnh.IsValidScore([(6, 4), (5, 7), (3, 3)], 3, SetTypes.NormalSet, SetTypes.MatchTieBreak),
        MatchWinnerTypes.NotDefined,
    )

    print("\nRESULTADO:", "TODOS OS TESTES PASSARAM" if ok else "HÁ FALHAS")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
