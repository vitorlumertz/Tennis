from fileReader import ReadInputFile
from fileSave import SaveFile
from tournament import Tournament

from tennisHelper import GetMaximumStage

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


if __name__ == '__main__':
  n = 7
  tournamentName = 'TournamentExample'
  # tournamentName = 'TournamentDoublesExample'
  tournament = ReadInputFile(f'.\\TestData\\{tournamentName}{n}.txt')
  PrintMatches(tournament)
  # tournament.StartCategories()
  tournament.UpdateBrackets()
  PrintBrackets(tournament)
  # SaveFile(f'.\\TestData\\{tournamentName}{n}Output.txt', tournament)