from fileReader import ReadInputFile
from fileSave import SaveFile
from tournament import Tournament


def PrintBrackets(tournament: Tournament):
  for category in tournament.categories.values():
    print(category.name)
    for key, nextKey in category.bracket.items():
      print(key, nextKey)


if __name__ == '__main__':
  n = 3
  tournamentName = 'TournamentExample'
  tournamentName = 'TournamentDoublesExample'
  tournament = ReadInputFile(f'.\\TestData\\{tournamentName}{n}.txt')
  tournament.InitializeCategories()
  tournament.UpdateBrackets()
  SaveFile(f'.\\TestData\\{tournamentName}{n}Output.txt', tournament)