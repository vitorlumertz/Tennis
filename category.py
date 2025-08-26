import tennisHelper as tnh
from tennisEnums import *
from matchTeams import Team, Player, Double
from match import Match
from tennisExceptions import *
import itertools
import random
import math
import random
from copy import deepcopy


class Category:
  def __init__(
    self,
    name: str,
    categoryType: CategoryTypes,
    matchType: MatchTypes = MatchTypes.Single,
    isGroupsFinished: bool = False,
    isRandomDoubles: bool = False,
    isInitialized: bool = False,
    players: dict[str, Player] | None = None,
    teams: dict[str, Team] | None = None,
    groups: list[list[Team]] | None = None,
  ):
    self.name = name
    self.categoryType = categoryType
    self.matchType = matchType
    self.isGroupsFinished = isGroupsFinished
    self.isRandomDoubles = isRandomDoubles
    self.isInitialized = isInitialized
    self.teams = {} if teams is None else teams
    self.players = {} if players is None else players
    self.groups = groups
    self.matches: dict[str, Match] = {}
    self.bracket: dict[str, str] = {}


  def AddTeam(self, team:Team):
    if isinstance(team, Double) and self.matchType is MatchTypes.Single:
      raise AddingDoubleInSingleCategory(team.name, self.name)

    if isinstance(team, Player) and self.matchType is MatchTypes.Double:
      dictToAdd = self.players
    else:
      dictToAdd = self.teams

    if team.name in dictToAdd:
      raise DuplicatedTeam(team.name, self.name)
    else:
      dictToAdd[team.name] = team


  def GetPlayer(self, playerName:str) -> Player|None:
    return self.players.get(playerName)


  def GetMatches(self, key:str='') -> dict[str,Match]:
    if key == '':
      return self.matches
    matches = {}
    for matchKey, match in self.matches.items():
      if key in matchKey:
        matches[matchKey] = match
    return matches


  def SortTeams(self):
    def GetSortingValues(team:Team):
      return (
        team.seedNumber == 0,
        team.seedNumber,
        team.name,
      )

    def Sort(items:dict):
      return sorted(items.items(), key=lambda item: GetSortingValues(item[1]))

    self.players = dict(Sort(self.players))
    self.teams = dict(Sort(self.teams))


  def SortMatches(self):
    if self.categoryType is CategoryTypes.Groups:
      self.matches = {k: self.matches[k] for k in sorted(self.matches.keys(), key=lambda x: tnh.GetMatchSortCriteria(x))}


  def UpdateCategoryType(self):
    if (self.categoryType == CategoryTypes.Automatic) and (self.teams is not None):
      n = len(self.teams)
      if n < 6:
        self.categoryType = CategoryTypes.RoundRobin
      elif n < 10:
        self.categoryType = CategoryTypes.Groups
      else:
        self.categoryType = CategoryTypes.SingleElimination


  def GetNumberOfGroups(self):
    n = len(self.teams)
    groupsOf4 = n % 3
    groupsOf3 = math.floor(n / 3) - groupsOf4
    return groupsOf3, groupsOf4


  def GetNonSeeds(self):
    nonSeeds = [team for team in self.teams.values() if not team.isSeed]
    return random.sample(nonSeeds, len(nonSeeds))


  def GetSeeds(self):
    seeds = []
    if self.categoryType == CategoryTypes.Groups:
      groupsOf3, groupsOf4 = self.GetNumberOfGroups()
      maxSeeds = groupsOf3 + groupsOf4
    else:
      maxSeeds = tnh.GetTournamentStage(len(self.teams))
    if maxSeeds is None:
      return seeds
    for team in self.teams.values():
      if team.isSeed:
        seeds.append((team.seedNumber, team))

    numSeeds = len(seeds)
    if numSeeds >= maxSeeds:
      seeds = sorted(seeds, key=lambda x: x[0])
      finalSeeds = seeds[:maxSeeds]
      newNonSeeds = seeds[maxSeeds:]
      for seed in newNonSeeds:
        seed[1].isSeed = False
      return [seed[1] for seed in finalSeeds]

    missingSeeds = maxSeeds - numSeeds
    drawnSeeds = self.GetNonSeeds()[:missingSeeds]
    for ds in drawnSeeds:
      ds.isSeed = True

    seeds = sorted(seeds, key=lambda x: x[0])
    seeds = [seed[1] for seed in seeds]
    seeds.extend(drawnSeeds)
    return seeds


  def GetNumberOfByes(self, numTeams=None):
    numTeams = len(self.teams) if numTeams is None else numTeams
    maxTeams = tnh.CeilPowerOfTwo(numTeams)
    return maxTeams - numTeams


  def GetByes(self, numSeeds, numTeams=None):
    numByes = self.GetNumberOfByes(numTeams)
    if numByes <= numSeeds:
      numByesWithSeeds = numByes
      numByesWithoutSeeds = 0
    else:
      numByesWithSeeds = numSeeds
      numByesWithoutSeeds = numByes - numByesWithSeeds
    return numByesWithSeeds, numByesWithoutSeeds


  def AddGroupMatches(self, teams, sets, setType, lastSetType, groupNumber=None):
    matches = list(itertools.combinations(teams, 2))
    if self.categoryType == CategoryTypes.RoundRobin:
      keyPrefix = str(len(matches)).zfill(3) + 'GU'
    else:
      keyPrefix = str(groupNumber).zfill(3) + 'GR'
    for matchNum, matchTeams in enumerate(matches):
      matchId = keyPrefix + str(matchNum+1).zfill(3)
      self.matches[matchId] = Match(matchTeams[0], matchTeams[1], sets=sets, setType=setType, lastSetType=lastSetType, isTeam1Set=True, isTeam2Set=True)


  def GetFirstRound(self, sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak):
    self.UpdateCategoryType()
    if self.categoryType == CategoryTypes.RoundRobin:
      self.AddGroupMatches(list(self.teams.values()), sets, setType, lastSetType)

    elif self.categoryType == CategoryTypes.SingleElimination:
      seeds = self.GetSeeds()
      nonSeeds = self.GetNonSeeds()
      numByesWithSeeds, numByesWithoutSeeds = self.GetByes(len(seeds))
      matchesKeys = tnh.GetMatchesKeys(len(self.teams))
      firstRound_aux = tnh.GetSeedsPositions(len(self.teams), len(seeds))
      byesWithoutSeedsCount = 0
      for i, match in enumerate(firstRound_aux):
        matchKey = matchesKeys[i]
        seedNumber = match[0] if match[1] is None else match[1]
        team1 = None
        team2 = None
        if seedNumber is not None:
          team1 = seeds[seedNumber - 1]
          if seedNumber > numByesWithSeeds:
            team2 = nonSeeds.pop()
        else:
          team1 = nonSeeds.pop()
          if byesWithoutSeedsCount < numByesWithoutSeeds:
            byesWithoutSeedsCount += 1
          else:
            team2 = nonSeeds.pop()

        self.matches[matchKey] = Match(team1, team2, sets=sets, setType=setType, lastSetType=lastSetType, isTeam1Set=True, isTeam2Set=True)

    elif self.categoryType == CategoryTypes.Groups:
      if not self.groups:
        seeds = self.GetSeeds()
        nonSeeds = self.GetNonSeeds()
        groupsOf3, groupsOf4 = self.GetNumberOfGroups()
        nGroups = groupsOf3 + groupsOf4
        groups = [[] for _ in range(nGroups)]
        for group in groups:
          group.append(seeds.pop())
        g = 0
        while len(nonSeeds) > 0:
          groups[g].append(nonSeeds.pop())
          g += 1
          if g >= nGroups:
            g = 0
        groups.reverse()
        self.groups = groups
      for i, group in enumerate(self.groups):
        self.AddGroupMatches(group, sets, setType, lastSetType, i+1)


  def GetBracket(self):
    bracket = {}
    if self.categoryType == CategoryTypes.SingleElimination:
      n = len(self.teams)
    elif self.categoryType == CategoryTypes.Groups:
      numClassified = 2
      n = numClassified * len(self.groups)
    else:
      return
    firstRoundKeys = tnh.GetMatchesKeys(n)
    for key in firstRoundKeys:
      stage = int(key[:3])
      while stage > 1:
        nextKey, _ = tnh.GetNextMatchKey(key)
        bracket[key] = nextKey
        if nextKey in bracket:
          break
        key = nextKey
        stage = int(key[:3])

    bracket['001FP001'] = None
    self.bracket = bracket


  def CompleteMatches(self, sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak):
    for key in self.bracket:
      if key not in self.matches:
        self.matches[key] = Match(None, None, sets=sets, setType=setType, lastSetType=lastSetType)


  def GetGroupClassification(self, i: int):
    matchKeyPrefix = str(i+1).zfill(3) + 'GR'
    matches = []
    for matchKey, match in self.matches.items():
      if (matchKey[:5] == matchKeyPrefix):
        matches.append(match)

    return tnh.GetClassification(matches)


  def UpdateBraket(self):
    for matchKey, match in self.matches.items():
      if matchKey[3:5] != 'FP':
        continue
      if match.matchWinner is MatchWinnerTypes.Team1:
        winner = match.team1
      elif match.matchWinner is MatchWinnerTypes.Team2:
        winner = match.team2
      elif match.matchWinner is MatchWinnerTypes.kNone:
        winner = None
      else:
        continue
      nextMatchKey, position = tnh.GetNextMatchKey(matchKey)
      if nextMatchKey is not None:
        nextMatch = self.matches[nextMatchKey]
        if position == 0:
          nextMatch.SetTeam(1, winner)
        else:
          nextMatch.SetTeam(2, winner)

        if (nextMatch.IsTeamsSet()) and ((nextMatch.team1 is None) or (nextMatch.team2 is None)):
          nextMatch.SetScore()

    if (self.categoryType is not CategoryTypes.Groups) or (self.isGroupsFinished):
      return

    classified = {}
    for i, group in enumerate(self.groups):
      groupClassification, isFinalClassification = self.GetGroupClassification(i)
      if isFinalClassification:
        classifiedNames = list(groupClassification.keys())[:2]
        first = {classifiedNames[0]: groupClassification[classifiedNames[0]]}
        second = {classifiedNames[1]: groupClassification[classifiedNames[1]]}
        classified.update({i+1: (first, second)})
      else:
        break
    else:
      self.isGroupsFinished = True
      firstClassified = {}
      firstGroupDict = {}
      for group, clf in classified.items():
        firstGroupDict.update({next(iter(clf[0].keys())): group})
        firstClassified.update(clf[0])
      firstClassified = tnh.SortClassification(firstClassified)
      finalClassification = []
      for playerName in firstClassified.keys():
        group = firstGroupDict[playerName]
        first = self.teams[playerName]
        second = self.teams[next(iter(classified[group][1].keys()))]
        finalClassification.append((first, second))

      seeds = [i[0] for i in finalClassification]
      numSeeds = len(seeds)
      numTeams = numSeeds * 2
      seedsPosition = tnh.GetSeedsPositions(numTeams, numSeeds)
      secondsUp = []
      secondsDown = []
      stage = len(seedsPosition)
      for i, match_aux in enumerate(seedsPosition):
        seedNumber = match_aux[0] if match_aux[1] is None else match_aux[1]
        if seedNumber is not None:
          second = finalClassification[seedNumber-1][1]
          if (i+1) / stage <= 0.5:
            secondsDown.append(second)
          else:
            secondsUp.append(second)

      numByesWithSeeds, _ = self.GetByes(numSeeds, numTeams)
      matchesKeys = tnh.GetMatchesKeys(numTeams)
      for i, match_aux in enumerate(seedsPosition):
        matchKey = matchesKeys[i]
        match = self.matches[matchKey]
        seedNumber = match_aux[0] if match_aux[1] is None else match_aux[1]
        isMatchWithSeed = False if seedNumber is None else True
        if isMatchWithSeed:
          match.SetTeam(1, seeds[seedNumber - 1])
          if seedNumber <= numByesWithSeeds:
            match.SetTeam(2, None)
            match.SetScore()
            continue
        else:
          if (i+1) / stage <= 0.5:
            match.SetTeam(1, secondsUp.pop(random.randint(0, len(secondsUp)-1)))
          else:
            match.SetTeam(1, secondsDown.pop(random.randint(0, len(secondsDown)-1)))
        if (i+1) / stage <= 0.5:
          match.SetTeam(2, secondsUp.pop(random.randint(0, len(secondsUp)-1)))
        else:
          match.SetTeam(2, secondsDown.pop(random.randint(0, len(secondsDown)-1)))


  def DrawDubles(self, oldDoubles: list[tuple[str,str]]):

    def RemoveDefinedDoublePlayers() -> dict[str,Player]:
      playersToDraw = deepcopy(self.players)
      for double in self.teams.values():
        playersToDraw.pop(double.player1.name)
        playersToDraw.pop(double.player2.name)
      return playersToDraw


    def DuplicateOldDoubles() -> list[tuple[str,str]]:
      inverseDoubles = [(d[1], d[0]) for d in oldDoubles]
      return oldDoubles + inverseDoubles


    def GetSeedSum(playersToDraw: dict[str,Player]) -> int:
      seedValues = [player.seedNumber for player in playersToDraw.values()]
      return min(seedValues) + max(seedValues)


    def GetSeedGroups(playersToDraw: dict[str,Player]) -> dict[int,list[Player]]:
      seedGroups = {}
      for player in playersToDraw.values():
        seedGroups.setdefault(player.seedNumber, []).append(player)
      return seedGroups


    def GetDrawDoubles(seedGroups:dict[int,list[Player]], seedSum:int) -> list[tuple[str,str]]:
      drawDoubles = []
      drawGroups = []
      for seedNum, players in seedGroups.items():
        if seedNum in drawGroups:
          continue

        otherSeedNum = seedSum - seedNum

        if otherSeedNum == seedNum:
          if len(players) % 2 != 0:
            raise DrawingDoublesError(self.name)
          random.shuffle(players)
          for i in range(1, len(players), 2):
            drawDoubles.append((players[i-1].name, players[i].name))
          drawGroups.extend([seedNum])

        else:
          otherPlayers = seedGroups[seedSum - seedNum]
          if len(players) != len(otherPlayers):
            raise DrawingDoublesError(self.name)
          random.shuffle(players)
          random.shuffle(otherPlayers)
          for i, player in enumerate(players):
            drawDoubles.append((player.name, otherPlayers[i].name))
          drawGroups.extend([seedNum, otherSeedNum])

      return drawDoubles


    def HasDuplicatedDouble(drawDoubles:list[tuple[str,str]], oldDoubles:list[tuple[str,str]]) -> bool:
      for double in drawDoubles:
        if double in oldDoubles:
          return True
      return False

    playersToDraw = RemoveDefinedDoublePlayers()
    duplicatedOldDoubles = DuplicateOldDoubles()
    seedGroups = GetSeedGroups(playersToDraw)
    seedSum = GetSeedSum(playersToDraw)

    maxIter = 10 ** 3
    for _ in range(maxIter):
      drawDoubles = GetDrawDoubles(seedGroups, seedSum)
      if not HasDuplicatedDouble(drawDoubles, duplicatedOldDoubles):
        random.shuffle(drawDoubles)
        for double in drawDoubles:
          player1 = self.GetPlayer(double[0])
          player2 = self.GetPlayer(double[1])
          self.AddTeam(Double(player1, player2))
        return
    else:
      raise DrawingDoublesError(self.name)