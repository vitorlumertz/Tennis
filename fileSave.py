from tournament import *
from tennisEnums import *
from matchTeams import *


def GetSectionTitle(section: FileSections):
  return '[' + section.name.upper() + ']\n'


def GetSectionComments(section: FileSections):
  comments = '//'
  if section is FileSections.Tournament:
    comments += 'Name, Number of Sets, Set Type, Last Set Type\n'
  elif section is FileSections.Categories:
    comments += 'Name, Category Type, Match Type, Is Groups Finished, Random Doubles, Initialized\n'
  elif section is FileSections.Players:
    comments += 'Name, Category, Seed Number, Is Seed\n'
  elif section is FileSections.OldDoubles:
    comments += 'Player 1, Player 2\n'
  elif section is FileSections.Doubles:
    comments += 'Player 1, Player 2, Category, Seed Number, Is Seed\n'
  elif section is FileSections.Groups:
    comments += 'Category, Group, Player\n'
  elif section is FileSections.Matches:
    comments += 'Category, Key, Player 1, Player 2, Score, Score Type, Sets, Set Type, Last Set Type, Is Players Set\n'
  return comments


def InitializeSection(file, section: FileSections):
  file.write(GetSectionTitle(section))
  file.write(GetSectionComments(section))


def ScoreToString(score):
  if score is None:
    return 'None'
  scoreStr = ''
  for i, set in enumerate(score):
    if i > 0:
      scoreStr += ' '
    scoreStr += str(set[0]) + 'x' + str(set[1])
  return scoreStr


def WriteTournamentSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.Tournament)
  text = tournament.name + ','
  text += str(tournament.sets) + ','
  text += tournament.setType.name + ','
  text += tournament.lastSetType.name + '\n\n'
  file.write(text)


def WriteCategoriesSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.Categories)
  for category in tournament.categories.values():
    category.SortMatches()
    text = category.name + ','
    text += category.categoryType.name + ','
    text += category.matchType.name + ','
    if category.isGroupsFinished:
      text += str(category.isGroupsFinished)
    text += ','
    if category.isRandomDoubles:
      text += str(category.isRandomDoubles)
    text += ','
    if category.isInitialized:
      text += str(category.isInitialized)
    text += '\n'
    file.write(text)
  file.write('\n')


def WritePlayersSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.Players)
  for category in tournament.categories.values():
    if category.matchType is MatchTypes.Single:
      players = category.teams
    else:
      players = category.players
    for player in players.values():
      text = player.name + ','
      text += category.name + ','
      text += str(player.seedNumber) + ','
      text += str(player.isSeed) + '\n'
      file.write(text)
    file.write('\n')


def WriteOldDoublesSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.OldDoubles)
  for double in tournament.oldDoubles:
    file.write(double[0] + ',' + double[1] + '\n')
  file.write('\n')


def WriteDoublesSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.Doubles)
  for category in tournament.categories.values():
    if category.matchType is MatchTypes.Double:
      doubles: dict[str, Double] = category.teams
      for double in doubles.values():
        text = double.player1.name + ','
        text += double.player2.name + ','
        text += category.name + ','
        text += str(double.seedNumber) + ','
        text += str(double.isSeed) + '\n'
        file.write(text)
    file.write('\n')


def WriteGroupsSection(file, tournament: Tournament):
  sectionInitialized = False
  for category in tournament.categories.values():
    if category.groups is not None:
      if not sectionInitialized:
        InitializeSection(file, FileSections.Groups)
        sectionInitialized = True
      for i, group in enumerate(category.groups):
        for player in group:
          text = category.name + ','
          text += str(i+1) + ','
          text += player.name + '\n'
          file.write(text)
        file.write('\n')


def WriteMatchesSection(file, tournament: Tournament):
  InitializeSection(file, FileSections.Matches)
  for category in tournament.categories.values():
    for key, match in category.matches.items():
      matchProperties = [category.name]
      matchProperties.append(key)
      matchProperties.append(match.team1.name if match.team1 is not None else 'None')
      matchProperties.append(match.team2.name if match.team2 is not None else 'None')
      matchProperties.append(ScoreToString(match.score) if match.score is not None else '')
      matchProperties.append(match.scoreType.name if not match.scoreType == ScoreTypes.NotDefined else '')
      matchProperties.append(str(match.sets) if match.sets != tournament.sets else '')
      matchProperties.append(match.setType.name if match.setType != tournament.setType else '')
      matchProperties.append(match.lastSetType.name if match.lastSetType != tournament.lastSetType else '')
      matchProperties.append('True' if match.isTeamsSet else '')
      file.write(','.join(matchProperties))
      file.write('\n')
    file.write('\n')


def SaveFile(fileName, tournament):
  with open(fileName, 'w') as file:
    WriteTournamentSection(file, tournament)
    WriteCategoriesSection(file, tournament)
    WritePlayersSection(file, tournament)
    WriteOldDoublesSection(file, tournament)
    WriteDoublesSection(file, tournament)
    WriteGroupsSection(file, tournament)
    WriteMatchesSection(file, tournament)