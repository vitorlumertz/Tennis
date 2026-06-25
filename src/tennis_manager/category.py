import tennis_manager.tennisHelper as tnh
from tennis_manager.classification import Classification, DEFAULT_CLASSIFICATION_CRITERIA, ResultPoints
from tennis_manager.classification import Columns as ClassificationCols
from tennis_manager.groupClassification import GetBracketWithTeams, GetTeams
from tennis_manager.matchTeams import Team, Player, Double, NormalizeTeamName
from tennis_manager.match import Match
from tennis_manager.matchKey import MatchKey, MatchKeyType, GetStageMatchKeys
from tennis_manager.tennisEnums import *
from tennis_manager.tennisExceptions import *

import itertools
import random
from copy import deepcopy
from collections import defaultdict


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
    groupClassificationType: GroupClassificationTypes | None = None,
    numOfclassifiedsInGroups: int = 0,
    groupDrawType: GroupDrawTypes = GroupDrawTypes.ByGroupSize,
    groupDrawQuantity: int = 3,
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
    self.groupClassificationType = groupClassificationType
    self.numOfclassifiedsInGroups = numOfclassifiedsInGroups
    self.groupDrawType = groupDrawType
    self.groupDrawQuantity = groupDrawQuantity
    self.matches: dict[str, Match] = {}
    self.bracket: dict[str, str] = {}
    self.__ValidateGroupDrawSettings()


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
    return self.players.get(NormalizeTeamName(playerName))


  def GetTeamsSummary(self, isPlayers=False) -> str:
    if isPlayers and self.matchType is MatchTypes.Double:
      teams = self.players
    else:
      teams = self.teams
    summary = f"Quantidade total: {len(teams)}\n\n"
    seedNumbersCount = defaultdict(int)
    for team in teams.values():
      seedNumbersCount[team.seedNumber] += 1
    for t in sorted(seedNumbersCount.items()):
      seedNumber, count = t
      summary += f"Quantidade de cabeças de chave nº {seedNumber}: {count}\n"

    return summary


  def GetMatches(self, key:MatchKey|None=None) -> dict[str,Match]:
    if key is None:
      return self.matches
    matches = {}
    for m in self.matches.values():
      if m.matchKey.IsSameStage(key):
        matches[m.matchKey.name] = m
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
    matchKeys = [m.matchKey for m in self.matches.values()]
    self.matches = {mk.name: self.matches[mk.name] for mk in sorted(matchKeys, key=lambda x: x.GetMatchSortCriteria())}


  def UpdateCategoryType(self) -> None:
    if self.teams is None:
      return

    n = len(self.teams)

    if self.categoryType == CategoryTypes.Automatic:
      if n < 6:
        self.categoryType = CategoryTypes.RoundRobin
      elif n < 10:
        self.categoryType = CategoryTypes.Groups
      else:
        self.categoryType = CategoryTypes.SingleElimination

    elif (
      self.categoryType == CategoryTypes.Groups
      and (
        n < 3
        or (
          self.groupDrawType == GroupDrawTypes.ByGroupSize
          and self.GetNumberOfTotalGroups() == 1
        )
      )
    ):
      self.categoryType = CategoryTypes.RoundRobin


  def HasEliminatoryStage(self) -> bool:
    return self.categoryType is not CategoryTypes.RoundRobin


  def __ValidateGroupDrawSettings(self, numTeams:int|None=None) -> None:
    if self.groupDrawType is GroupDrawTypes.ByGroupSize:
      if self.groupDrawQuantity < 3:
        raise ValueError(f"Group size must be greater than or equal to 3. {self.groupDrawQuantity} was given.")
      return

    if self.groupDrawQuantity < 1:
      raise ValueError(f"Number of groups must be greater than or equal to 1. {self.groupDrawQuantity} was given.")

    if numTeams is not None and numTeams // self.groupDrawQuantity < 3:
      raise ValueError(f"Number of groups ({self.groupDrawQuantity}) creates groups with fewer than 3 teams in category {self.name}.")


  def GetNumberOfGroups(self) -> tuple[int, int]:
    n = len(self.teams)
    self.__ValidateGroupDrawSettings(n)

    if self.groupDrawType is GroupDrawTypes.ByGroupSize:
      nGroups = max(1, n // self.groupDrawQuantity)
    else:
      nGroups = self.groupDrawQuantity

    largerGroups = n % nGroups
    smallerGroups = nGroups - largerGroups

    if (largerGroups == 0) and (self.groupDrawType is GroupDrawTypes.ByGroupSize) and (nGroups * self.groupDrawQuantity < n):
      largerGroups = nGroups
      smallerGroups = 0

    return smallerGroups, largerGroups


  def GetNumberOfTotalGroups(self) -> int:
    smallerGroups, largerGroups = self.GetNumberOfGroups()
    return smallerGroups + largerGroups


  def GetNonSeeds(self):
    nonSeeds = [team for team in self.teams.values() if not team.isSeed]
    return random.sample(nonSeeds, len(nonSeeds))


  def GetSeeds(self):
    seeds = []
    if self.categoryType == CategoryTypes.Groups:
      maxSeeds = self.GetNumberOfTotalGroups()
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


  def GetByes(self, numSeeds:int, numTeams:int|None=None) -> tuple[int, int]:
    numTeams = len(self.teams) if numTeams is None else numTeams
    return tnh.GetByes(numSeeds, numTeams)


  def AddGroupMatches(self, teams, sets, setType, lastSetType, groupNumber=None):
    matches = list(itertools.combinations(teams, 2))
    if self.categoryType == CategoryTypes.RoundRobin:
      fi = len(matches)
      stage = MatchKeyType.RoundRobin
    else:
      fi = groupNumber
      stage = MatchKeyType.Groups
    for matchNum, matchTeams in enumerate(matches):
      ti = matchNum + 1
      matchKey = MatchKey(firstInfo=fi, stageType=stage, thirdInfo=ti)
      self.matches[matchKey.name] = Match(matchTeams[0], matchTeams[1], sets=sets, setType=setType, lastSetType=lastSetType, isTeam1Set=True, isTeam2Set=True, matchKey=matchKey)


  def GetFirstRound(self, sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak):
    self.UpdateCategoryType()
    if self.categoryType == CategoryTypes.RoundRobin:
      group = list(self.teams.values())
      self.groups = [group]
      self.AddGroupMatches(group, sets, setType, lastSetType)

    elif self.categoryType == CategoryTypes.SingleElimination:
      seeds = self.GetSeeds()
      nonSeeds = self.GetNonSeeds()
      numByesWithSeeds, numByesWithoutSeeds = self.GetByes(len(seeds))
      matchesKeys = GetStageMatchKeys(len(self.teams))
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

        self.matches[matchKey.name] = Match(team1, team2, sets=sets, setType=setType, lastSetType=lastSetType, isTeam1Set=True, isTeam2Set=True, matchKey=matchKey)

    elif self.categoryType == CategoryTypes.Groups:
      if not self.groups:
        seeds = self.GetSeeds()
        nonSeeds = self.GetNonSeeds()
        nGroups = self.GetNumberOfTotalGroups()
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


  def __GetNumberOfClassifiedsInGroups(self) -> int:
    if self.groupClassificationType is None:
      self.groupClassificationType = GroupClassificationTypes.TwoPerGroup

    if self.groupClassificationType == GroupClassificationTypes.TwoPerGroup:
      return 2 * len(self.groups)

    if self.groupClassificationType == GroupClassificationTypes.OnePerGroup:
      return len(self.groups)

    if self.groupClassificationType == GroupClassificationTypes.TwoG4_OneG3:
      if self.groups is None:
        raise ValueError(f"Expected a list[list[Team]] for groups in category {self.name}, got None.")

      groupSizes = [len(group) for group in self.groups]
      if (max(groupSizes) > 4) or (min(groupSizes) < 3):
        raise ValueError(f"Category {self.name} has group classification type = TwoG4_OneG3, but not all groups are of these sizes.")

      return sum(2 if s == 4 else 1 for s in groupSizes)

    if self.numOfclassifiedsInGroups < len(self.groups):
      raise ValueError(f"Number of classified teams in groups is less than the number of groups in category {self.name}.")

    return self.numOfclassifiedsInGroups


  def GetBracket(self) -> None:
    bracket = {}
    if self.categoryType == CategoryTypes.SingleElimination:
      n = len(self.teams)
    elif self.categoryType == CategoryTypes.Groups:
      n = self.__GetNumberOfClassifiedsInGroups()
    else:
      return
    firstRoundKeys = GetStageMatchKeys(n)
    for key in firstRoundKeys:
      stage = key.firstInfo
      while stage > 1:
        nextKey, _ = key.NextKey()
        bracket[key.name] = nextKey.name
        if nextKey.name in bracket:
          break
        key = nextKey
        stage = key.firstInfo

    bracket[f'001{MatchKeyType.SingleElimination.value}001'] = None
    self.bracket = bracket


  def CompleteMatches(self, sets=3, setType=SetTypes.NormalSet, lastSetType=SetTypes.MatchTieBreak) -> None:
    for key in self.bracket:
      if key not in self.matches:
        self.matches[key] = Match(None, None, sets=sets, setType=setType, lastSetType=lastSetType, matchKey=MatchKey(key))


  def GetGroupMatches(self, groupNumber:int|None=None) -> list[Match]:
    if self.categoryType == CategoryTypes.RoundRobin:
      return list(self.matches.values())

    matches = [
      m for m in self.matches.values()
      if m.matchKey.IsGroups()
    ]

    if groupNumber is not None:
      matches = [m for m in matches if m.matchKey.firstInfo == groupNumber + 1]

    return matches


  def GetClassification(
    self,
    groupNumber:int|None=None,
    classificationCriteria:list[ClassificationCols]|None=None,
    resultPoints:ResultPoints|None=None,
  ) -> Classification:
    matches = self.GetGroupMatches(groupNumber)
    sortColumns = (classificationCriteria if classificationCriteria is not None else DEFAULT_CLASSIFICATION_CRITERIA).copy()
    groups = self.groups if self.categoryType is CategoryTypes.Groups else None
    return Classification(matches, sortColumns, groups, resultPoints)


  def UpdateBracket(
    self,
    classificationCriteria:list[ClassificationCols]|None=None,
    resultPoints:ResultPoints|None=None,
  ) -> None:
    for m in self.matches.values():
      if not m.matchKey.IsSingleElimination():
        continue

      if m.matchWinner is MatchWinnerTypes.Team1:
        winner = m.team1
      elif m.matchWinner is MatchWinnerTypes.Team2:
        winner = m.team2
      elif m.matchWinner is MatchWinnerTypes.kNone:
        winner = None
      else:
        continue
      nextMatchKey, position = m.matchKey.NextKey()
      if nextMatchKey is not None:
        nextMatch = self.matches[nextMatchKey.name]
        if position == 0:
          nextMatch.SetTeam(1, winner)
        else:
          nextMatch.SetTeam(2, winner)

        if (nextMatch.IsTeamsSet()) and ((nextMatch.team1 is None) or (nextMatch.team2 is None)):
          nextMatch.SetScore()

    if (self.categoryType is CategoryTypes.RoundRobin) and (self.groups is not None) and (not self.isGroupsFinished):
      self.isGroupsFinished = self.GetClassification(classificationCriteria=classificationCriteria, resultPoints=resultPoints).isFinalized

    if (self.categoryType is CategoryTypes.Groups) and (self.groups is not None) and (not self.isGroupsFinished):
      classification = self.GetClassification(classificationCriteria=classificationCriteria, resultPoints=resultPoints)
      self.isGroupsFinished = classification.isFinalized

      if classification.isFinalized:
        nClassifieds = self.__GetNumberOfClassifiedsInGroups()
        if nClassifieds <= self.GetNumberOfTotalGroups() * 2:
          bracket = GetBracketWithTeams(GetTeams(classification, nClassifieds))
        else:
          seedsPositions = tnh.GetSeedsPositions(nClassifieds, nClassifieds)

          # logica duplicada com groupClassification.py
          bracket = []
          for pos1, pos2 in seedsPositions:
            team1 = None
            team2 = None
            if pos1 is not None:
              team1 = classification.GetTeamNameByPosition(pos1)
            if pos2 is not None:
              team2 = classification.GetTeamNameByPosition(pos2)
            bracket.append((team1, team2))
          # fim da logica duplicada

        stage = len(bracket)
        for i, match_aux in enumerate(bracket, start=1):
          matchKey = MatchKey(firstInfo=stage, stageType=MatchKeyType.SingleElimination, thirdInfo=i)
          match = self.matches[matchKey.name]
          t1 = self.teams[match_aux[0]] if match_aux[0] else None
          t2 = self.teams[match_aux[1]] if match_aux[1] else None
          match.SetTeam(1, t1)
          match.SetTeam(2, t2)
          if (t1 is None) or (t2 is None):
            match.SetScore()

        self.UpdateBracket(classificationCriteria, resultPoints)


  def GetFirstEliminationStage(self) -> int|None:
    stages = [m.matchKey.firstInfo for m in self.matches.values() if m.matchKey.IsSingleElimination()]
    if len(stages) == 0:
      return None
    return max(stages)


  def DrawDubles(self, oldDoubles: list[tuple[str,str]]):

    def Pop(playersToDraw:dict[str,Player], playerName:str) -> None:
      try:
        playersToDraw.pop(playerName)
      except KeyError:
        raise PlayerNotFound(playerName, self.name)

    def RemoveDefinedDoublePlayers() -> dict[str,Player]:
      playersToDraw = deepcopy(self.players)
      for double in self.teams.values():
        Pop(playersToDraw, double.player1.name)
        Pop(playersToDraw, double.player2.name)
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
