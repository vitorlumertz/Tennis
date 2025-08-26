from tennisEnums import *
from match import Match
from matchTeams import Team


def IsValidSetScore(setScore: tuple, setType=SetTypes.NormalSet) -> bool:
  if setScore[0] == setScore[1]:
    return False

  if setType == SetTypes.NotDefined:
    return True

  winnerScore = setScore[0]
  loserScore = setScore[1]
  if winnerScore < loserScore:
    winnerScore = setScore[1]
    loserScore = setScore[0]

  normalWinScore = 6
  if setType == SetTypes.ShortSet:
    normalWinScore = 4
  elif setType == SetTypes.LongSet:
    normalWinScore = 8
  elif setType == SetTypes.MatchTieBreak:
    normalWinScore = 10
    if winnerScore < normalWinScore :
      return False
    if (winnerScore == normalWinScore) and (loserScore in range(normalWinScore-1)):
      return True
    if (winnerScore > normalWinScore) and (loserScore == winnerScore - 2):
      return True
    return False

  if (winnerScore == normalWinScore) and (loserScore in range(normalWinScore-1)):
    return True
  if (winnerScore == normalWinScore + 1) and (loserScore in range(normalWinScore-1, normalWinScore+1)):
    return True
  return False


def IsValidScore(score: list, sets: int, setType=SetTypes.NormalSet) -> MatchWinnerTypes:
  if (
    (score is None) or
    (sets % 2 == 0) or
    (len(score) > sets)
  ):
    return MatchWinnerTypes.NotDefined

  for set in score:
    if not IsValidSetScore(set, setType):
      return MatchWinnerTypes.NotDefined

  setsToBeWon = int(sets/2 + 0.5)

  p1SetsWon = 0
  p2SetsWon = 0
  for set in score:
    if set[0] > set[1]:
      p1SetsWon += 1
    else:
      p2SetsWon += 1

  if (p1SetsWon == setsToBeWon) and (p2SetsWon < setsToBeWon):
    return MatchWinnerTypes.Team1

  if (p2SetsWon == setsToBeWon) and (p1SetsWon < setsToBeWon):
    return MatchWinnerTypes.Team2

  return MatchWinnerTypes.NotDefined


def CeilPowerOfTwo(n, result=1):
  if n <= result:
    return result
  return CeilPowerOfTwo(n, result*2)


def GetTournamentStage(numPlayers):
  maxPlayersStage = CeilPowerOfTwo(numPlayers)
  if maxPlayersStage <= 1:
    return None
  return int(maxPlayersStage/2)


def MatchKeysConversion(stage, list):
  prefix = str(stage).zfill(3) + 'FP'
  return [prefix + str(n).zfill(3) for n in list]


def GetMatchesKeys(numPlayers):
  stage = GetTournamentStage(numPlayers)
  return MatchKeysConversion(stage, range(1, stage+1))


def GetNextMatchKey(key):
  stage = int(key[:3])
  if stage == 1:
    return (None, None)
  n = int(key[5:])
  newStage = int(stage / 2)
  position = 1
  if n % 2 == 1:
    n += 1
    position = 0
  newN = int(n / 2)
  nextMatchKey = str(newStage).zfill(3) + 'FP' + str(newN).zfill(3)
  return nextMatchKey, position


def DeleteExtraSeeds(seedsPositions, numSeeds):
  newSeedsPositions = []
  for match in seedsPositions:
    p1 = match[0]
    p2 = match[1]
    if (p1 is not None) and (p1 > numSeeds):
      p1 = None
    if (p2 is not None) and (p2 > numSeeds):
      p2 = None
    newSeedsPositions.append((p1, p2))

  return newSeedsPositions


def GetSeedsPositions(numPlayers, numSeeds):
  draw = {}
  actualStage = 1
  draw[actualStage] = [(1, 2)]
  actualSeedsSum = 3
  while actualStage < numPlayers/2:
    stageMatches = []
    actualStage *= 2
    actualSeedsSum += actualStage
    for i in range(actualStage):
      if i % 2 == 0:
        j = int(i/2)
        k = 0
      else:
        j = int((i-1) / 2)
        k = 1
      oldSeed = draw[actualStage/2][j][k]
      newSeed = actualSeedsSum - oldSeed
      match_ = (oldSeed, newSeed) if i % 2 == 0 else (newSeed, oldSeed)
      stageMatches.append(match_)
    draw[actualStage] = stageMatches

  return DeleteExtraSeeds(draw[actualStage], numSeeds)


def GetSetGames(setType: SetTypes):
  return {
    SetTypes.NormalSet: 6,
    SetTypes.LongSet: 8,
    SetTypes.ShortSet: 4,
    SetTypes.MatchTieBreak: 10,
  }.get(setType)


def GetTeamsFromMatches(matches:list[Match]) -> set[Team]:
  teams = set()
  for match in matches:
    if match.team1 not in teams:
      teams.add(match.team1)
    if match.team2 not in teams:
      teams.add(match.team2)
  return teams


def GetMatchBalances(match:Match):
  setBalance = 0
  gameBalance = 0
  if (match.matchWinner is MatchWinnerTypes.kNone) or (match.matchWinner is MatchWinnerTypes.NotDefined):
    return setBalance, gameBalance

  for set in match.score:
    if set[0] > set[1]:
      setBalance += 1
    else:
      setBalance -= 1
    gameBalance += set[0] - set[1] # pontos do tiebreakao nao estao entrando aqui?

  return setBalance, gameBalance


def GetTiebreakerCriteria(classificationPlayer):
  return (
    classificationPlayer['Victories'],
    classificationPlayer['SetBalance'],
    classificationPlayer['GameBalance'],
  )


def SortClassification(classification):
  playersCriteria = [(player, GetTiebreakerCriteria(criteria)) for player, criteria in classification.items()]
  playersCriteria = sorted(playersCriteria, key=lambda x: x[1], reverse=True)
  finalClassification = {}
  for player, _ in playersCriteria:
    finalClassification.update({player: classification[player]})

  return finalClassification


def GetClassification(matches:list[Match]):
  teams = GetTeamsFromMatches(matches)
  classification = {}
  for team in teams:
    classification[team.name] = {
      'Victories': 0,
      'SetBalance': 0,
      'GameBalance': 0,
    }

  isFinalClassification = True
  for m in matches:
    setBalance, gameBalance = GetMatchBalances(m)

    if m.matchWinner is MatchWinnerTypes.Team1:
      classification[m.team1.name]['Victories'] += 1
    elif m.matchWinner is MatchWinnerTypes.Team2:
      classification[m.team2.name]['Victories'] += 1
    else:
      isFinalClassification = False

    classification[m.team1.name]['SetBalance'] += setBalance
    classification[m.team1.name]['GameBalance'] += gameBalance
    classification[m.team2.name]['SetBalance'] -= setBalance
    classification[m.team2.name]['GameBalance'] -= gameBalance

  classification = SortClassification(classification)

  return classification, isFinalClassification


def GetMatchSortCriteria(matchKey):
  firstNum = int(matchKey[:3])
  typeStr = matchKey[3:5]
  secondNum = int(matchKey[5:])

  if typeStr == 'GR':
    firstCriteria = 0
    secondCriteria = firstNum
  else:
    firstCriteria = 1
    secondCriteria = 1 / firstNum

  thirdCriteria = secondNum

  return((firstCriteria, secondCriteria, thirdCriteria))


def GetMaximumStage(matchesKeys:list[str]) -> int|None:
  keys =[int(matchKey[:3]) for matchKey in matchesKeys if "FP" in matchKey]
  if len(keys) == 0:
    return None
  return max([int(matchKey[:3]) for matchKey in matchesKeys if "FP" in matchKey])
