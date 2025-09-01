from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from category import Category
from match import Match
from tennisEnums import CategoryTypes


def ExportGroupCategoryToPdf(category:Category, filePath:str):
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