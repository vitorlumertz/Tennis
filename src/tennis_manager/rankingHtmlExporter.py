from html import escape
from typing import Any, TypedDict
import pandas as pd

from tennis_manager.category import Category
from tennis_manager.ranking import Ranking, RankingColumns


class CategoryRegistration(TypedDict):
  name: str
  count: int


class StageRegistration(TypedDict):
  stage: int
  name: str
  total: int
  categories: list[CategoryRegistration]


CHART_COLORS = [
  "#d8aaa3",
  "#9bb7c8",
  "#a8bf9d",
  "#d6bd86",
  "#b9a7c8",
  "#c5b8a8",
  "#c9988f",
  "#93aaa4",
]

MAX_BAR_HEIGHT = 210


def __GetCategoryRegistrationCount(category:Category) -> int:
  if len(category.teams) > 0:
    return len(category.teams)

  return len(category.players)


def __GetRegistrationsByStage(ranking:Ranking) -> list[StageRegistration]:
  stages: list[StageRegistration] = []
  for stageNumber, tournament in enumerate(ranking.tournaments.values(), start=1):
    categories: list[CategoryRegistration] = []
    total = 0
    for category in tournament.categories.values():
      count = __GetCategoryRegistrationCount(category)
      total += count
      categories.append({
        "name": category.name,
        "count": count,
      })

    stages.append({
      "stage": stageNumber,
      "name": f"Etapa {stageNumber}",
      "total": total,
      "categories": categories,
    })

  return stages


def __FormatRankingValue(value:Any) -> str:
  if pd.isna(value):
    return "0"

  try:
    numericValue = float(value)
  except (TypeError, ValueError):
    return escape(str(value))

  if numericValue.is_integer():
    return str(int(numericValue))

  return f"{numericValue:g}"


def __GetHtmlRankingRows(categoryDf:pd.DataFrame, stageColumns:list[str]) -> str:
  rows: list[str] = []
  for _, row in categoryDf.iterrows():
    position = int(row[RankingColumns.Position.name])
    isInitiallyHidden = position > 5
    hiddenClass = " is-hidden" if isInitiallyHidden else ""
    stageCells = "".join(
      f"<td>{__FormatRankingValue(row[stageColumn])}</td>"
      for stageColumn in stageColumns
    )
    discardedValue = row[RankingColumns.DiscardedValue.name]
    discardedClass = "discarded-value" if not pd.isna(discardedValue) and discardedValue > 0 else "muted-value"
    discardedText = __FormatRankingValue(discardedValue) if not pd.isna(discardedValue) and discardedValue > 0 else "-"
    rows.append(
      "<tr"
      f" class=\"ranking-row{hiddenClass}\""
      f" data-position=\"{position}\""
      ">"
      f"<td class=\"position-cell\">{position}</td>"
      f"<td class=\"name-cell\">{escape(str(row[RankingColumns.Name.name]))}</td>"
      f"<td class=\"points-cell\">{__FormatRankingValue(row[RankingColumns.Points.name])}</td>"
      f"{stageCells}"
      f"<td class=\"{discardedClass}\">{discardedText}</td>"
      "</tr>"
    )

  return "\n".join(rows)


def __GetHtmlRankingSections(ranking:Ranking, stageColumns:list[str]) -> str:
  sections: list[str] = []
  stageHeaders = "".join(f"<th>Etapa {escape(stageColumn)}</th>" for stageColumn in stageColumns)
  stageColumnWidths = "".join("<col class=\"score-col\">" for _ in stageColumns)
  tableMinWidth = 394 + (64 * len(stageColumns))
  for categoryName, categoryDf in ranking.data.groupby(RankingColumns.Category.name, sort=False):
    categoryId = f"category-{len(sections)}"
    hasExpandableRows = (categoryDf[RankingColumns.Position.name] > 5).any()
    toggleInput = ""
    toggleButton = ""
    if hasExpandableRows:
      toggleInput = f"<input class=\"category-toggle\" id=\"{categoryId}-toggle\" type=\"checkbox\">"
      toggleButton = (
        f"<label class=\"toggle-button\" for=\"{categoryId}-toggle\">"
        "<span class=\"toggle-show-complete\">Ver classificacao completa</span>"
        "<span class=\"toggle-show-top\">Ver apenas top 5</span>"
        "</label>"
      )

    sections.append(
      f"<section class=\"category-section\" id=\"{categoryId}\">"
      f"{toggleInput}"
      "<div class=\"category-header\">"
      f"<h2>{escape(str(categoryName))}</h2>"
      f"{toggleButton}"
      "</div>"
      "<div class=\"table-wrap\">"
      f"<table style=\"min-width: {tableMinWidth}px;\">"
      "<colgroup>"
      "<col class=\"position-col\">"
      "<col class=\"name-col\">"
      "<col class=\"total-col\">"
      f"{stageColumnWidths}"
      "<col class=\"discard-col\">"
      "</colgroup>"
      "<thead>"
      "<tr>"
      "<th>Pos.</th>"
      "<th>Nome</th>"
      "<th>Total</th>"
      f"{stageHeaders}"
      "<th>Descarte</th>"
      "</tr>"
      "</thead>"
      "<tbody>"
      f"{__GetHtmlRankingRows(categoryDf, stageColumns)}"
      "</tbody>"
      "</table>"
      "</div>"
      "</section>"
    )

  return "\n".join(sections)


def __GetHtmlRegistrationsChart(ranking:Ranking) -> str:
  registrations = __GetRegistrationsByStage(ranking)
  categoryNames: list[str] = []
  for stage in registrations:
    for category in stage["categories"]:
      if category["name"] not in categoryNames:
        categoryNames.append(category["name"])

  colorByCategory = {
    categoryName: CHART_COLORS[index % len(CHART_COLORS)]
    for index, categoryName in enumerate(categoryNames)
  }
  maxTotal = max([stage["total"] for stage in registrations] or [1])

  chartColumns: list[str] = []
  for stage in registrations:
    barHeight = (stage["total"] / maxTotal) * MAX_BAR_HEIGHT if stage["total"] > 0 else 0
    segments: list[str] = []
    for category in stage["categories"]:
      segmentHeight = (category["count"] / stage["total"]) * 100 if stage["total"] > 0 else 0
      categoryName = escape(category["name"])
      categoryCount = category["count"]
      categoryColor = colorByCategory[category["name"]]
      segments.append(
        "<div"
        " class=\"bar-segment\""
        f" style=\"height: {segmentHeight:.6g}%; background: {categoryColor};\""
        f" title=\"{categoryName}: {categoryCount}\""
        ">"
        f"{categoryCount if categoryCount > 0 else ''}"
        "</div>"
      )

    chartColumns.append(
      "<div class=\"chart-column\">"
      f"<div class=\"chart-total\">{stage['total']}</div>"
      f"<div class=\"bar\" style=\"height: {barHeight:.6g}px;\">"
      f"{''.join(segments)}"
      "</div>"
      f"<div class=\"chart-label\" title=\"{escape(stage['name'])}\">{escape(stage['name'])}</div>"
      "</div>"
    )

  legendItems = "".join(
    "<span class=\"legend-item\">"
    f"<span class=\"legend-swatch\" style=\"background: {colorByCategory[categoryName]};\"></span>"
    f"<span>{escape(categoryName)}</span>"
    "</span>"
    for categoryName in categoryNames
  )

  return (
    "<section class=\"chart-section\">"
    "<div class=\"section-title\">"
    "<h2>Inscritos por etapa</h2>"
    "</div>"
    "<div class=\"chart\">"
    f"<div class=\"chart-bars\">{''.join(chartColumns)}</div>"
    f"<div class=\"legend\">{legendItems}</div>"
    "</div>"
    "</section>"
  )


def ExportToHtml(ranking:Ranking, filePath:str) -> None:
  stageColumns = ranking.GetStageColumns()
  html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(ranking.name)} - Classificacao</title>
  <style>
    :root {{
      --ink: #252424;
      --muted: #6d6664;
      --line: #e6ddda;
      --paper: #fffdfb;
      --surface: #f7f1ee;
      --red: #9f4d45;
      --red-soft: #d8aaa3;
      --red-faint: #f2dfdc;
      --shadow: rgba(83, 48, 43, 0.08);
      font-family: Arial, Helvetica, sans-serif;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
    }}

    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 42px;
    }}

    header {{
      border-bottom: 1px solid var(--line);
      margin-bottom: 24px;
      padding-bottom: 18px;
    }}

    h1, h2 {{
      margin: 0;
      letter-spacing: 0;
    }}

    h1 {{
      font-size: 30px;
      line-height: 1.18;
    }}

    h2 {{
      font-size: 19px;
      line-height: 1.25;
    }}

    .category-section, .chart-section {{
      margin-top: 24px;
    }}

    .category-header, .section-title {{
      align-items: center;
      display: flex;
      gap: 14px;
      justify-content: space-between;
      margin-bottom: 10px;
    }}

    .toggle-button {{
      background: var(--red-faint);
      border: 1px solid var(--red-soft);
      border-radius: 6px;
      color: #65352f;
      cursor: pointer;
      font-weight: 700;
      min-height: 34px;
      padding: 7px 11px;
    }}

    .toggle-button:hover {{
      background: #ead1cc;
    }}

    .category-toggle {{
      height: 1px;
      opacity: 0;
      position: absolute;
      width: 1px;
    }}

    .toggle-show-top {{
      display: none;
    }}

    .category-toggle:checked ~ .category-header .toggle-show-complete {{
      display: none;
    }}

    .category-toggle:checked ~ .category-header .toggle-show-top {{
      display: inline;
    }}

    .table-wrap {{
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 8px 24px var(--shadow);
      overflow-x: auto;
    }}

    table {{
      border-collapse: separate;
      border-spacing: 0;
      table-layout: fixed;
      width: 100%;
    }}

    .position-col {{
      width: 52px;
    }}

    .name-col {{
      width: 190px;
    }}

    .total-col, .discard-col {{
      width: 74px;
    }}

    .score-col {{
      width: 64px;
    }}

    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: right;
      white-space: nowrap;
    }}

    th {{
      background: var(--surface);
      color: #4a403e;
      font-size: 13px;
      text-transform: uppercase;
    }}

    th:nth-child(2), td:nth-child(2) {{
      text-align: left;
    }}

    th:nth-child(1), td:nth-child(1),
    th:nth-child(2), td:nth-child(2) {{
      position: sticky;
      z-index: 2;
    }}

    th:nth-child(1), td:nth-child(1) {{
      left: 0;
    }}

    th:nth-child(2), td:nth-child(2) {{
      left: 52px;
    }}

    th:nth-child(1), th:nth-child(2) {{
      z-index: 4;
    }}

    td:nth-child(1), td:nth-child(2) {{
      background: var(--paper);
      box-shadow: 1px 0 0 var(--line);
    }}

    tr:last-child td {{
      border-bottom: 0;
    }}

    .ranking-row.is-hidden {{
      display: none;
    }}

    .category-toggle:checked ~ .table-wrap .ranking-row.is-hidden {{
      display: table-row;
    }}

    .position-cell {{
      color: var(--red);
      font-weight: 700;
    }}

    .name-cell {{
      font-weight: 700;
      line-height: 1.2;
      overflow-wrap: anywhere;
      white-space: normal;
    }}

    .points-cell {{
      background: var(--red-faint);
      color: #5f302b;
      font-size: 17px;
      font-weight: 800;
    }}

    .discarded-value {{
      color: var(--red);
      font-weight: 700;
    }}

    .muted-value {{
      color: #a69a96;
    }}

    .chart {{
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 8px 24px var(--shadow);
      padding: 16px;
      overflow-x: auto;
    }}

    .chart-bars {{
      align-items: flex-end;
      border-bottom: 1px solid var(--line);
      display: flex;
      gap: 18px;
      min-height: 280px;
      min-width: 100%;
      padding: 10px 4px 0;
    }}

    .chart-column {{
      align-items: center;
      display: flex;
      flex-direction: column;
      flex: 0 0 76px;
      height: 270px;
      justify-content: flex-end;
      width: 76px;
    }}

    .chart-total {{
      color: #473f3d;
      font-weight: 700;
      margin-bottom: 6px;
      min-height: 18px;
      text-align: center;
    }}

    .bar {{
      align-items: stretch;
      background: #f2ece9;
      border-radius: 7px 7px 0 0;
      display: flex;
      flex-direction: column-reverse;
      overflow: hidden;
      width: 46px;
    }}

    .bar-segment {{
      align-items: center;
      color: #211f1e;
      display: flex;
      font-size: 12px;
      font-weight: 700;
      justify-content: center;
      min-height: 2px;
      overflow: hidden;
      padding: 2px 0;
      text-overflow: ellipsis;
      white-space: nowrap;
      width: 100%;
    }}

    .chart-label {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      margin-top: 8px;
      max-width: 76px;
      overflow: hidden;
      text-align: center;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      margin-top: 16px;
    }}

    .legend-item {{
      align-items: center;
      color: var(--muted);
      display: inline-flex;
      font-size: 13px;
      gap: 6px;
    }}

    .legend-swatch {{
      border-radius: 3px;
      display: inline-block;
      height: 12px;
      width: 12px;
    }}

    @media (max-width: 720px) {{
      main {{
        width: min(100% - 20px, 1180px);
        padding-top: 22px;
      }}

      h1 {{
        font-size: 24px;
      }}

      .category-header {{
        align-items: flex-start;
        flex-direction: column;
      }}

      .chart-bars {{
        gap: 14px;
        min-height: 240px;
      }}

      .chart-column {{
        flex-basis: 64px;
        height: 230px;
        width: 64px;
      }}

      .bar {{
        width: 40px;
      }}

      .chart-label {{
        max-width: 64px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escape(ranking.name)}</h1>
    </header>
    {__GetHtmlRankingSections(ranking, stageColumns)}
    {__GetHtmlRegistrationsChart(ranking)}
  </main>
</body>
</html>
"""
  with open(filePath, "w", encoding="utf-8") as file:
    file.write(html)


if __name__ == '__main__':
  from tennis_manager.fileReader import ReadInputFile
  tournaments = [
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\1aEtapa\RankingDeDuplas2026_1aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\2aEtapa\RD_2026_2aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\3aEtapa\RD3aEtapa_8.txt"),
  ]
  ranking = Ranking('Ranking de Duplas 2026', tournaments, discardWorstValue=False)
  ExportToHtml(ranking, "RD2026.html")
