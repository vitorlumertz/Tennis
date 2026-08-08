from tennis_manager.fileReader import ReadInputFile
from tennis_manager.fileSave import SaveFile
from tennis_manager.tournament import Tournament
from tennis_manager.ranking import Ranking
from tennis_manager.rankingHtmlExporter import ExportToHtml


def PrintBrackets(tournament: Tournament):
  for category in tournament.categories.values():
    print(category.name)
    for key, nextKey in category.bracket.items():
      print(key, nextKey)


def PrintMatches(tournament: Tournament):
  for category in tournament.categories.values():
    print(category.name)
    for match in category.matches.values():
      data = (
        match.team1.name if match.team1 is not None else "",
        match.team2.name if match.team2 is not None else "",
        match.PrintScore(),
      )
      print(data)
    print()


def ExportRankingToHtml():
  tournaments = [
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\1aEtapa\RankingDeDuplas2026_1aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\2aEtapa\RD_2026_2aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\3aEtapa\RD3aEtapa_8.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\4aEtapa\RD4aEtapa_9.txt"),
  ]
  ranking = Ranking('Ranking de Duplas 2026', tournaments, discardWorstValue=False)
  ExportToHtml(ranking, "RD2026.html")


def RunCleanCopy():
  t = ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\4aEtapa\RD4aEtapa_9.txt")
  copied = t.CleanCopy("RD5aEtapa")
  SaveFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\5aEtapa\RD5aEtapa_0.txt", copied)


if __name__ == '__main__':
  #n = 5
  #tournamentName = 'TournamentExample'
  #tournamentName = 'TournamentDoublesExample'
  #tournament = ReadInputFile(f'.\\TestData\\{tournamentName}{n}.txt')
  # PrintMatches(tournament)
  # tournament.StartCategories()
  # tournament.UpdateBrackets()
  # PrintBrackets(tournament)
  # SaveFile(f'.\\TestData\\{tournamentName}{n}Output.txt', tournament)
  #from GoogleSheets.tournamentExport import ExportTournamentToGoogleSheets
  #ExportTournamentToGoogleSheets(tournament, "InscricoesTeste1", "1Va2dpkfftGt0RFTnp1rt4x0A23fD6h2K", {"A":8,"B":4})

  RunCleanCopy()
