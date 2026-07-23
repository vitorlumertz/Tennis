from __future__ import annotations
from typing import TYPE_CHECKING

from tennis_manager.tennisEnums import *
from tennis_manager.matchTeams import Team

if TYPE_CHECKING:
  from tennis_manager.match import Match


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


def GetSetType(setIndex:int, sets:int, setType:SetTypes, lastSetType:SetTypes) -> SetTypes:
  if (sets > 1) and (setIndex == sets - 1):
    return lastSetType
  return setType


def IsValidScore(score: list, sets: int, setType=SetTypes.NormalSet, lastSetType=SetTypes.NormalSet) -> MatchWinnerTypes:
  if (
    (score is None) or
    (sets % 2 == 0) or
    (len(score) > sets)
  ):
    return MatchWinnerTypes.NotDefined

  for i, set in enumerate(score):
    currentSetType = GetSetType(i, sets, setType, lastSetType)
    if not IsValidSetScore(set, currentSetType):
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


def GetNumberOfByes(numTeams:int) -> int:
  maxTeams = CeilPowerOfTwo(numTeams)
  return maxTeams - numTeams


def GetByes(numSeeds:int, numTeams:int) -> tuple[int, int]:
  numByes = GetNumberOfByes(numTeams)
  if numByes <= numSeeds:
    numByesWithSeeds = numByes
    numByesWithoutSeeds = 0
  else:
    numByesWithSeeds = numSeeds
    numByesWithoutSeeds = numByes - numByesWithSeeds
  return numByesWithSeeds, numByesWithoutSeeds


def DeleteExtraSeeds(seedsPositions, numSeeds):
  def ProcessPlayer(player:int|None) -> int|None:
    if (player is not None) and (player > numSeeds):
      return None
    return player

  newSeedsPositions = []
  for match in seedsPositions:
    p1 = ProcessPlayer(match[0])
    p2 = ProcessPlayer(match[1])
    newSeedsPositions.append((p1, p2))

  return newSeedsPositions


def GetSeedsPositions(numPlayers:int, numSeeds:int, numMatches:int|None=None) -> list[tuple[int|None, int|None]]:
  draw = {}
  actualStage = 1
  draw[actualStage] = [(1, 2)]
  actualSeedsSum = 3
  limit = numMatches or numPlayers/2
  while actualStage < limit:
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
  def Add(team:Team|None) -> None:
    nonlocal teams
    if team is not None:
      teams.add(team)

  teams = set()
  for match in matches:
    Add(match.team1)
    Add(match.team2)
  return teams


def GetStageName(stage:int) -> str:
  stageName = {
    1: "Final",
    2: "Semifinal",
    4: "Quartas de Final",
    8: "Oitavas de Final",
    16: "R32",
    32: "R64",
    64: "R128",
    128: "R256",
  }.get(stage)

  if stageName is None:
    raise ValueError(f"Error getting stage name for value {stage}.")

  return stageName