from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from typing import Literal

from tennis_manager.category import Category
from tennis_manager.match import Match
from tennis_manager.tennisEnums import CategoryTypes, MatchWinnerTypes, ScoreTypes
from tennis_manager.tennisHelper import GetStageName


def ExportGroupCategoryToPdf(category:Category, filePath:str) -> None:
  def GetTeamNameStr(i, name):
    return f"{i+1}. {name}\n"

  def GetMatchStr(i, match:Match):
    return f"{i+1}. {match.team1.name} x {match.team2.name}\n"

  title = f"Categoria {category.name}"
  groupsContent = []
  if category.categoryType is CategoryTypes.Groups:
    for groupNumber, groupTeams in enumerate(category.groups):
      text = f"Grupo {groupNumber + 1}:\n\n"
      for i, team in enumerate(groupTeams):
        text += GetTeamNameStr(i, team.name)

      text += f"\nJogos do Grupo {groupNumber + 1}:\n\n"
      for i, match in enumerate(category.GetGroupMatches(groupNumber)):
        text += GetMatchStr(i, match)

      groupsContent.append(text)

  elif category.categoryType is CategoryTypes.RoundRobin:
    text = "Grupo Único:\n\n"
    for i, teamName in enumerate(category.teams.keys()):
      text += GetTeamNameStr(i, teamName)

    text += "\nJogos:\n\n"
    for i, match in enumerate(category.matches.values()):
      text += GetMatchStr(i, match)

    groupsContent.append(text)

  file = canvas.Canvas(filePath, pagesize=A4)
  width, height = A4

  y = height - 40
  file.setFont("Helvetica-Bold", 14)
  file.drawString(50, y, title)
  file.setFont("Helvetica", 12)
  y -= 20
  rowsCounter = 0
  for text in groupsContent:
    rows = text.split('\n')
    rowsCounter += len(rows)
    if rowsCounter > 36:
      file.showPage()
      rowsCounter = len(rows)
      y = height - 50
    for row in rows:
      y -= 20
      file.drawString(50, y, row)
  file.save()


def ExportSingleEliminationCategoryToPdf(category:Category, filePath:str) -> None:
  if category.categoryType is not CategoryTypes.SingleElimination:
    raise ValueError("Expected a SingleElimination category.")

  firstStage = category.GetFirstEliminationStage()
  if firstStage is None:
    raise ValueError("Expected int, got None in category.GetFirstEliminationStage().")

  stages = []
  stage = firstStage
  while stage >= 1:
    stages.append(stage)
    stage //= 2
  pageSize = landscape(A4)
  pdf = canvas.Canvas(filePath, pagesize=pageSize)
  width, height = pageSize
  marginX, top, bottom = 28, 58, 28
  gap = 16
  columnWidth = (width - 2 * marginX - gap * (len(stages) - 1)) / len(stages)
  slotHeight = (height - top - bottom) / firstStage
  boxHeight = min(31, max(14, slotHeight * .72))
  fontSize = min(9, max(5.5, boxHeight * .28))

  pdf.setTitle(category.name)
  pdf.setFont("Helvetica-Bold", 15)
  pdf.drawCentredString(width / 2, height - 25, f"Categoria {category.name}")

  matchesByPosition = {
    (match.matchKey.firstInfo, match.matchKey.thirdInfo): match
    for match in category.matches.values()
  }

  def GetTeamName(match:Match, teamNum:Literal[1, 2]) -> str:
    team = match.team1 if teamNum == 1 else match.team2
    isTeamSet = match.isTeam1Set if teamNum == 1 else match.isTeam2Set

    if isTeamSet:
      name = team.name if team is not None else "BYE"
      if (
        (teamNum == 1 and match.scoreType is ScoreTypes.T1Forfeit)
        or (teamNum == 2 and match.scoreType is ScoreTypes.T2Forfeit)
      ):
        name += " (Des)"
      if (
        match.scoreType is ScoreTypes.DoubleWO
        or (teamNum == 1 and match.scoreType is ScoreTypes.WO_to_T2)
        or (teamNum == 2 and match.scoreType is ScoreTypes.WO_to_T1)
      ):
        name += " (WO)"
      return name
    return ""

  def Fit(text, maxWidth, fontName="Helvetica"):
    if stringWidth(text, fontName, fontSize) <= maxWidth:
      return text
    suffix = "..."
    while text and stringWidth(text + suffix, fontName, fontSize) > maxWidth:
      text = text[:-1]
    return text + suffix

  def GetTeamResult(match:Match, teamNum:Literal[1, 2]) -> str:
    if match.score is None:
      return ""
    scoreIndex = teamNum - 1
    return " ".join(str(setScore[scoreIndex]) for setScore in match.score)

  def IsWinner(match:Match, teamNum:Literal[1, 2]) -> bool:
    expectedWinner = MatchWinnerTypes.Team1 if teamNum == 1 else MatchWinnerTypes.Team2
    return match.matchWinner is expectedWinner

  positions = {}
  for column, stage in enumerate(stages):
    x = marginX + column * (columnWidth + gap)
    pdf.setFont("Helvetica-Bold", 9)
    stageTitle = GetStageName(stage)
    pdf.drawCentredString(x + columnWidth / 2, height - 44, stageTitle)

    for matchNumber in range(1, stage + 1):
      centerY = height - top - (matchNumber - .5) * (firstStage / stage) * slotHeight
      y = centerY - boxHeight / 2
      match = matchesByPosition[(stage, matchNumber)]
      positions[(stage, matchNumber)] = (x, centerY)

      pdf.setStrokeColorRGB(.25, .25, .25)
      pdf.rect(x, y, columnWidth, boxHeight, stroke=1, fill=0)
      pdf.line(x, centerY, x + columnWidth, centerY)
      padding = 4
      names = (GetTeamName(match, 1), GetTeamName(match, 2))
      results = (GetTeamResult(match, 1), GetTeamResult(match, 2))
      resultWidth = max(
        stringWidth(result, "Helvetica-Bold", fontSize)
        for result in results
      )
      resultGap = 6 if resultWidth > 0 else 0
      maxTextWidth = columnWidth - 2 * padding - resultWidth - resultGap
      baselineOffset = max(fontSize * .35, boxHeight * .18)
      baselines = (
        centerY + baselineOffset,
        centerY - baselineOffset - fontSize * .55,
      )
      for teamNum in (1, 2):
        index = teamNum - 1
        fontName = "Helvetica-Bold" if IsWinner(match, teamNum) else "Helvetica"
        pdf.setFont(fontName, fontSize)
        pdf.drawString(
          x + padding,
          baselines[index],
          Fit(names[index], maxTextWidth, fontName),
        )
        if results[index]:
          pdf.setFont("Helvetica", fontSize)
          pdf.drawRightString(
            x + columnWidth - padding,
            baselines[index],
            results[index],
          )

  # Join pairs from each round to the match they feed in the following round.
  for stage in stages[:-1]:
    nextStage = stage // 2
    for matchNumber in range(1, stage + 1, 2):
      _, y1 = positions[(stage, matchNumber)]
      _, y2 = positions[(stage, matchNumber + 1)]
      nextX, nextY = positions[(nextStage, (matchNumber + 1) // 2)]
      currentX = positions[(stage, matchNumber)][0] + columnWidth
      elbowX = currentX + gap / 2
      pdf.line(currentX, y1, elbowX, y1)
      pdf.line(currentX, y2, elbowX, y2)
      pdf.line(elbowX, y2, elbowX, y1)
      pdf.line(elbowX, nextY, nextX, nextY)

  pdf.save()


def ExportCategoryToPdf(category:Category, filePath:str) -> None:
  if category.categoryType in (CategoryTypes.Groups, CategoryTypes.RoundRobin):
    return ExportGroupCategoryToPdf(category, filePath)
  if category.categoryType is CategoryTypes.SingleElimination:
    return ExportSingleEliminationCategoryToPdf(category, filePath)
  raise ValueError(f"Unsupported category type: {category.categoryType.name}.")
