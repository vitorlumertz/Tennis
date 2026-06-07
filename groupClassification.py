from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import Literal

from classification import Classification, Columns
import tennisHelper as tnh


class BracketSide(Enum):
  Up = 1
  Down = 2


@dataclass
class Team_aux:
  name: str
  position: int
  group: int

  def IsBye(self) -> bool:
    return self.group < 0


@dataclass
class TeamChoice:
  t1: Team_aux|None
  t2: Team_aux|None
  group: int
  chosen: Literal[0,1,2,3] = 0


  def OrderT1AndT2(self) -> None:
    if self.t2 is None:
      return

    if self.t2.position < self.t1.position:
      newT1 = deepcopy(self.t2)
      self.t2 = deepcopy(self.t1)
      self.t1 = newT1


  def IsDefined(self) -> bool:
    return self.chosen > 0


  def IsAnyTeamChosen(self) -> bool:
    return self.chosen == 1 or self.chosen == 2


  def ChosenNoTeam(self) -> bool:
    return self.chosen == 3


  def IsBye(self) -> bool:
    return self.group < 0


  def IsT1Alone(self) -> bool:
    return self.t2 is None


  def GetChosenPosition(self) -> int:
    if self.chosen == 1:
      return self.t1.position
    if self.chosen == 2:
      return self.t2.position
    return 0


class Choices:
  def __init__(self, teams:list[Team_aux]):
    teamChoicesPerGroup: dict[int, TeamChoice] = {}
    for t in teams:
      teamChoice = teamChoicesPerGroup.get(t.group)
      if teamChoice is None:
        teamChoicesPerGroup[t.group] = TeamChoice(t, None, t.group)
      else:
        teamChoice.t2 = t

    for c in teamChoicesPerGroup.values():
      c.OrderT1AndT2()

    self.up = deepcopy(teamChoicesPerGroup)
    self.down = deepcopy(teamChoicesPerGroup)
    self.stage = tnh.GetTournamentStage(len(teams))
    self.numSeeds = min(self.stage, self.Size())


  def IsDivisionFinished(self) -> bool:

    def Check(choices:dict[int, TeamChoice]) -> bool:
      for c in choices.values():
        if not c.IsDefined():
          return False
      return True

    return Check(self.up) and Check(self.down)


  def Size(self) -> int:
    return len(self.up)


  def __DefineSeed(self, seed:Literal[1,2]) -> None:
    choisesOfSeed = self.up
    otherChoises = self.down
    if seed == 2:
      choisesOfSeed = self.down
      otherChoises = self.up

    for g, c in choisesOfSeed.items():
      if c.t1.position == seed:
        c.chosen = 1
        otherChoice = otherChoises[g]
        if otherChoice.t2 is None:
          otherChoice.chosen = 3
        else:
          otherChoice.chosen = 2
        break


  def DefineSeeds1And2(self) -> None:
    self.__DefineSeed(1)
    self.__DefineSeed(2)


  def ChoicesWithT1AndT2NotDefined(self, side:BracketSide) -> int:
    choices = self.up if side is BracketSide.Up else self.down
    return len([c for c in choices.values() if not c.IsT1Alone() and not c.IsDefined()])


  def TeamsChosen(self, side:BracketSide) -> int:
    choices = self.up if side is BracketSide.Up else self.down
    return len([c for c in choices.values() if c.IsAnyTeamChosen()])


  def ChoicesDefinedWithNoTeam(self, side:BracketSide) -> int:
    choices = self.up if side is BracketSide.Up else self.down
    return len([c for c in choices.values() if c.ChosenNoTeam()])


  def GetChoicesT1AloneNotDefined(self, side:BracketSide) -> dict[int, TeamChoice]:
    choices = self.up if side is BracketSide.Up else self.down
    return {g: c for g, c in choices.items() if c.IsT1Alone() and not c.IsDefined()}


  def GetPositionsSum(self, side:BracketSide) -> int:
    choices = self.up if side is BracketSide.Up else self.down
    sumDefinedTeams = 0
    for c in choices.values():
      sumDefinedTeams += c.GetChosenPosition()

    return sumDefinedTeams


  def GetPositionsToChoose(self, side:BracketSide, byePosition:int|None) -> list[tuple[int, int|None]]:
    choices = self.up if side is BracketSide.Up else self.down
    positionsToChoose = []
    for c in choices.values():
      if not c.IsDefined():
        if c.IsT1Alone():
          positionsToChoose.append((c.t1.position, None))
        else:
          positionsToChoose.append((c.t1.position, c.t2.position))

    if byePosition is not None:
      positionsToChoose.append(byePosition)

    return positionsToChoose


  def DefineTeamByPosition(self, position:int, side:BracketSide=BracketSide.Up) -> None:
    choices = self.up if side is BracketSide.Up else self.down
    otherChoices = self.up if side is BracketSide.Down else self.down
    for g, c in choices.items():
      if not c.IsDefined():
        otherChoice = otherChoices[g]
        if c.t1.position == position:
          c.chosen = 1
          otherChoice.chosen = 3 if c.IsT1Alone() else 2
        elif (not c.IsT1Alone()) and (c.t2.position == position):
          c.chosen = 2
          otherChoice.chosen = 1


  def DefineTeamsByPositions(self, positions:list[int], side:BracketSide=BracketSide.Up) -> None:
    choices = self.up if side is BracketSide.Up else self.down
    otherChoices = self.up if side is BracketSide.Down else self.down
    positions.sort()
    for g, c in choices.items():
      if not c.IsDefined():
        otherChoice = otherChoices[g]
        if c.t1.position in positions:
          c.chosen = 1
          otherChoice.chosen = 3 if c.IsT1Alone() else 2
        else:
          otherChoice.chosen = 1
          c.chosen = 3 if c.IsT1Alone() else 2


  def ChangedSeedPositions(self, seedsPositions:list[tuple[int|None, int|None]]) -> bool:

    def Check(choices:dict[int, TeamChoice], seeds:list[int]) -> bool:
      for c in choices.values():
        if (c.chosen == 1) and (c.t1.position <= self.numSeeds) and (c.t1.position not in seeds):
          return True
      return False

    seedsUp = []
    seedsDown = []
    for i, match in enumerate(seedsPositions, start=1):
      listToUpdate = seedsUp if i / self.stage <= 0.5 else seedsDown
      if match[0] is not None:
        listToUpdate.append(match[0])
      if match[1] is not None:
        listToUpdate.append(match[1])

    changedSeedsPositions = Check(self.up, seedsUp)

    if changedSeedsPositions:
      return True

    return Check(self.down, seedsDown)


  def ObrigatoryChoices(self, teamsUp:int, teamsDown:int) -> None:

    def BySide(side:BracketSide, teams:int) -> None:
      otherChoices = self.up if side is BracketSide.Down else self.down

      choicesWithT1AndT2NotDefined = self.ChoicesWithT1AndT2NotDefined(side)
      teamsChosen = self.TeamsChosen(side)

      mustChoose = teams - choicesWithT1AndT2NotDefined - teamsChosen
      if mustChoose > 0:
        choicesT1AloneNotDefined = self.GetChoicesT1AloneNotDefined(side)
        if len(choicesT1AloneNotDefined) == mustChoose:
          for g, c in choicesT1AloneNotDefined.items():
            c.chosen = 1
            otherChoices[g].chosen = 3

    BySide(BracketSide.Up, teamsUp)
    BySide(BracketSide.Down, teamsDown)


  def GetMinAndMaxByes(self, side:BracketSide) -> tuple[int, int]:
    maxTeams = self.Size() - self.ChoicesDefinedWithNoTeam(side)
    minByes = max(0, self.stage - maxTeams)

    choicesWithT1AndT2NotDefined = self.ChoicesWithT1AndT2NotDefined(side)
    teamsChosen = self.TeamsChosen(side)
    maxByes = self.stage - teamsChosen - choicesWithT1AndT2NotDefined

    return minByes, maxByes


  def GetTeamsAux(self, side:BracketSide) -> list[Team_aux]:
    choices = self.up if side is BracketSide.Up else self.down
    teams: list[Team_aux] = []
    for c in choices.values():
      if c.chosen == 1:
        teams.append(c.t1)
      elif c.chosen == 2:
        teams.append(c.t2)

    return sorted(teams, key=lambda t: t.position)


def DivideUpAndDownTeams(teams:list[Team_aux]) -> Choices:
  choices = Choices(teams)
  choices.DefineSeeds1And2()

  numByes = tnh.GetNumberOfByes(len(teams))
  if numByes == 0:
    byesUp = 0
    byesDown = 0

  else:
    minByesUp, maxByesUp = choices.GetMinAndMaxByes(BracketSide.Up)
    minByesDown, maxByesDown = choices.GetMinAndMaxByes(BracketSide.Down)

    byesUp = minByesUp if minByesUp == maxByesUp else None
    byesDown = minByesDown if minByesDown == maxByesDown else None

    if byesUp is not None:
      byesDown = numByes - byesUp
    elif byesDown is not None:
      byesUp = numByes - byesDown

  teamsUp = None
  teamsDown = None

  if byesUp is not None:
    teamsUp = choices.stage - byesUp
    teamsDown = choices.stage - byesDown
    choices.ObrigatoryChoices(teamsUp, teamsDown)

  if choices.IsDivisionFinished():
    return choices

  seedsPositions = tnh.GetSeedsPositions(len(teams), choices.numSeeds)
  changedSeedsPositions = choices.ChangedSeedPositions(seedsPositions)

  if not changedSeedsPositions:
    positionsInBracket = tnh.GetSeedsPositions(len(teams), len(teams))
    positionsUp = []
    for match in positionsInBracket[:int(len(positionsInBracket)/2)]:
      if match[0] is not None:
        positionsUp.append(match[0])
      if match[1] is not None:
        positionsUp.append(match[1])

    for p in range(1, len(teams) + 1):
      side = BracketSide.Up if p in positionsUp else BracketSide.Down
      choices.DefineTeamByPosition(p, side)
      if teamsUp and teamsDown:
        choices.ObrigatoryChoices(teamsUp, teamsDown)

    if choices.IsDivisionFinished():
      return choices
    else:
      raise Exception("Expected choices to be finished.")

  byePosition = None
  if numByes % 2 == 1:
    byePosition = len(teams) + 1

  positionsToChooseUp = choices.GetPositionsToChoose(BracketSide.Up, byePosition)

  twoPlayersChoices = []
  onePlayerChoices = []
  for a, b in positionsToChooseUp:
    if b is None:
      onePlayerChoices.append(a)
    else:
      twoPlayersChoices.append((a, b))

  choicesPossibilitiesUp = []
  for positionsA in product(*twoPlayersChoices):
    if len(onePlayerChoices) == 0:
      choicesPossibilitiesUp.append(positionsA)
    else:
      for positionsB in combinations(onePlayerChoices, choices.stage - len(twoPlayersChoices)):
        choicesPossibilitiesUp.append(positionsA + positionsB)

  sumDefinedTeamsUp = choices.GetPositionsSum(BracketSide.Up)
  sumDefinedTeamsDown = choices.GetPositionsSum(BracketSide.Down)
  bestPossibilityUp = None
  bestDiff = None
  for choicesPossibilityUp in choicesPossibilitiesUp:
    totalSumUp = sumDefinedTeamsUp
    totalSumDown = sumDefinedTeamsDown
    for a, b in positionsToChooseUp:
      if a in choicesPossibilityUp:
        totalSumUp += a
        if b is not None:
          totalSumDown += b
      else:
        totalSumDown += a
        if b is not None:
          totalSumUp += b

    diff = abs(totalSumUp - totalSumDown)
    if (bestDiff is None) or (diff < bestDiff):
      bestDiff = diff
      bestPossibilityUp = choicesPossibilityUp

    if bestDiff == 0:
      break

  choices.DefineTeamsByPositions(list(bestPossibilityUp))

  if choices.IsDivisionFinished():
    return choices
  else:
    raise Exception("Expected choices to be finished.")


def GetTeams(classification:Classification, n:int) -> list[Team_aux]:
  teams = []
  for teamName, row in classification.classification.head(n).iterrows():
    teams.append(
      Team_aux(
        teamName,
        row[Columns.Position.name],
        row[Columns.Group.name],
      )
    )
  return teams


def GetBracketWithTeams(teams:list[Team_aux]) -> list[tuple[str|None, str|None]]:

  def BySide(side:BracketSide) -> list[tuple[str|None, str|None]]:
    sideTeams = choices.GetTeamsAux(side)
    seedsPositions = tnh.GetSeedsPositions(len(sideTeams), len(sideTeams), choices.stage/2)
    namesPositions = []

    for pos1, pos2 in seedsPositions:
      team1 = None
      team2 = None
      if pos1 is not None:
        team1 = sideTeams[pos1 - 1].name
      if pos2 is not None:
        team2 = sideTeams[pos2 - 1].name
      namesPositions.append((team1, team2))

    return namesPositions


  if len(teams) == 2:
    if teams[0].position < teams[1].position:
      return [(teams[0].name, teams[1].name)]
    return [(teams[1].name, teams[0].name)]

  choices = DivideUpAndDownTeams(teams)

  return BySide(BracketSide.Up) + BySide(BracketSide.Down)
