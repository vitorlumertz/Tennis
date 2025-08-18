from tournament import Tournament
from matchTeams import Player, Double
from category import Category
from match import Match
from tennisEnums import MatchTypes, CategoryTypes, SetTypes, ScoreTypes, FileSections


def CleanString(string:str, cleanSpaces=True, toUper=True):
  string = string.replace('\t', '')
  string = string.replace('\n', '')
  if cleanSpaces:
    string = string.replace(' ', '')
  if toUper:
    string = string.upper()
  return string


def EmptyLine(string):
  return CleanString(string, toUper=False) == ''


def CommentLine(string):
  return string[:2] == '//'


def CleanInfoLine(info):
  if EmptyLine(info[-1]):
    info.pop()
    CleanInfoLine(info)


def GetInfo(row:str):
  info = row.split(',')
  CleanInfoLine(info)
  return info


def GetSetType(string):
  string = CleanString(string)
  return {
    'NORMALSET': SetTypes.NormalSet,
    'SHORTSET': SetTypes.ShortSet,
    'LONGSET': SetTypes.LongSet,
    'MATCHTIEBREAK': SetTypes.MatchTieBreak,
  }.get(string, SetTypes.NotDefined)


def GetCategoryType(string):
  string = CleanString(string)
  return {
    'ROUNDROBIN': CategoryTypes.RoundRobin,
    'SINGLEELIMINATION': CategoryTypes.SingleElimination,
    'DOUBLEELIMINATION': CategoryTypes.DoubleElimination,
    'GROUPS': CategoryTypes.Groups,
    'TEAMS': CategoryTypes.Teams,
    'AUTOMATIC': CategoryTypes.Automatic,
  }.get(string)


def GetMatchType(string):
  string = CleanString(string)
  return {
    'SINGLE': MatchTypes.Single,
    'DOUBLE': MatchTypes.Double,
  }.get(string)


def GetScoreType(string):
  string = CleanString(string)
  return {
    'NORMAL': ScoreTypes.Normal,
    'WO_TO_T1': ScoreTypes.WO_to_T1,
    'WO_TO_T2': ScoreTypes.WO_to_T2,
    'DOUBLEWO': ScoreTypes.DoubleWO,
    'T1FORFEIT': ScoreTypes.T1Forfeit,
    'T2FORFEIT': ScoreTypes.T2Forfeit,
    'BYE_TO_T1': ScoreTypes.Bye_to_T1,
    'BYE_TO_T2': ScoreTypes.Bye_to_T2,
  }.get(string, ScoreTypes.NotDefined)


def GetBoolean(string):
  string = CleanString(string)
  return string == 'TRUE'


def GetScore(string):
  string = CleanString(string,cleanSpaces=False, toUper=False)
  sets = string.split(' ')
  score = []
  for set in sets:
    setGames = set.split('x')
    score.append((int(setGames[0]), int(setGames[1])))
  return score


def GetSection(string, actualSection):
  string = CleanString(string)
  return {
    '[RANKING]': FileSections.Ranking,
    '[TOURNAMENT]': FileSections.Tournament,
    '[CATEGORIES]': FileSections.Categories,
    '[PLAYERS]': FileSections.Players,
    '[OLDDOUBLES]': FileSections.OldDoubles,
    '[DOUBLES]': FileSections.Doubles,
    '[GROUPS]': FileSections.Groups,
    '[MATCHES]': FileSections.Matches,
    '[END]': FileSections.End,
  }.get(string, actualSection)


def ReadRanking(string):
  pass


def ReadTournament(string):
  info = GetInfo(string)
  name = CleanString(info[0], cleanSpaces=False, toUper=False)
  sets = int(CleanString(info[1], toUper=False))
  setType = GetSetType(info[2])
  lastSetType = GetSetType(info[3])
  return Tournament(name, sets, setType, lastSetType)


def ReadCategory(string, tournament: Tournament):
  info = GetInfo(string)
  name = CleanString(info[0], cleanSpaces=False, toUper=False)
  categoryType = GetCategoryType(info[1])
  matchType = GetMatchType(info[2])
  isGroupsfinished = False
  randomDoubles = False
  isInitialized = False
  if len(info) > 3:
    isGroupsfinished = GetBoolean(info[3])
  if len(info) > 4:
    randomDoubles = GetBoolean(info[4])
  if len(info) > 5:
    isInitialized = GetBoolean(info[5])
  category = Category(name, categoryType, matchType, isGroupsfinished, randomDoubles, isInitialized)
  tournament.AddCategory(category)


def ReadPlayer(string, tournament: Tournament):
  info = GetInfo(string)
  name = CleanString(info[0], cleanSpaces=False, toUper=False)
  categoryName = CleanString(info[1], cleanSpaces=False, toUper=False)
  seedNumber = 0
  isSeed = None
  if len(info) > 2:
    seedNumber = int(CleanString(info[2], toUper=False))
  if len(info) > 3:
    isSeed = GetBoolean(info[3])
  player = Player(name, seedNumber, isSeed)
  tournament.AddTeam(player, categoryName)


def ReadOldDouble(string, tournament: Tournament):
  info = GetInfo(string)
  name1 = CleanString(info[0], cleanSpaces=False, toUper=False)
  name2 = CleanString(info[1], cleanSpaces=False, toUper=False)
  tournament.AddOldDouble(name1, name2)


def ReadDouble(string, tournament: Tournament):
  def GetPlayer(category:Category, playerName:str) -> Player:
    player = category.GetPlayer(playerName)
    if player is None:
      return Player(playerName)
    return player

  info = GetInfo(string)
  player1Name = CleanString(info[0], cleanSpaces=False, toUper=False)
  player2Name = CleanString(info[1], cleanSpaces=False, toUper=False)
  categoryName = CleanString(info[2], cleanSpaces=False, toUper=False)
  seedNumber = 0
  isSeed = None
  if len(info) > 3:
    seedNumber = int(CleanString(info[3], toUper=False))
  if len(info) > 4:
    isSeed = GetBoolean(info[4])
  category = tournament.GetCategory(categoryName)
  player1 = GetPlayer(category, player1Name)
  player2 = GetPlayer(category, player2Name)
  double = Double(player1, player2, seedNumber, isSeed)
  tournament.AddTeam(double, categoryName)


def ReadGroup(string, tournament: Tournament):
  info = GetInfo(string)
  categoryName = CleanString(info[0], cleanSpaces=False, toUper=False)
  groupNumber = int(CleanString(info[1], toUper=False))
  playerName = CleanString(info[2], cleanSpaces=False, toUper=False)
  category = tournament.categories[categoryName]
  player = category.teams[playerName]
  if category.groups is None:
    category.groups = []
  if len(category.groups) < groupNumber:
    category.groups.append([])
  category.groups[groupNumber-1].append(player)


def ReadMatch(string, tournament: Tournament):
  info = GetInfo(string)
  categoryName = CleanString(info[0], cleanSpaces=False, toUper=False)
  category:Category = tournament.categories[categoryName]
  matchKey = CleanString(info[1])
  player1Name = CleanString(info[2], cleanSpaces=False, toUper=False)
  player2Name = CleanString(info[3], cleanSpaces=False, toUper=False)
  if player1Name == 'None':
    player1 = None
  else:
    player1 = category.teams[player1Name]
  if player2Name == 'None':
    player2 = None
  else:
    player2 = category.teams[player2Name]

  if (len(info) > 4) and ((info[4] != 'None') and (info[4] != '')):
    score = GetScore(info[4])
  else:
    score = None
  if len(info) > 5:
    scoreType = GetScoreType(info[5])
  else:
    scoreType = ScoreTypes.NotDefined
  if (len(info) > 6) and (info[6] != ''):
    sets = int(CleanString(info[6], toUper=False))
  else:
    sets = tournament.sets
  if (len(info) > 7) and (info[7] != ''):
    setType = GetSetType(info[7])
  else:
    setType = tournament.setType
  if (len(info) > 8) and (info[8] != ''):
    lastSetType = GetSetType(info[8])
  else:
    lastSetType = tournament.lastSetType
  isTeamsSet = False
  if (len(info) > 9) and (info[9] != ''):
    isTeamsSet = GetBoolean(info[9])

  category.matches[matchKey] = Match(player1, player2, score, scoreType, sets, setType, lastSetType, isTeamsSet)


def ReadInputFile(filePath) -> Tournament:
  tournament = None
  with open(filePath) as file:
    section = None
    for row in file:
      if EmptyLine(row) or CommentLine(row):
        continue

      newSection = GetSection(row, section)
      if newSection != section:
        section = newSection
        continue

      if section == FileSections.Ranking:
        ReadRanking(row)
      elif section == FileSections.Tournament:
        tournament = ReadTournament(row)
      elif section == FileSections.Categories:
        ReadCategory(row, tournament)
      elif section == FileSections.Players:
        ReadPlayer(row, tournament)
      elif section == FileSections.OldDoubles:
        ReadOldDouble(row, tournament)
      elif section == FileSections.Doubles:
        ReadDouble(row, tournament)
      elif section == FileSections.Groups:
        ReadGroup(row, tournament)
      elif section == FileSections.Matches:
        ReadMatch(row, tournament)
      elif section == FileSections.End:
        break

  return tournament