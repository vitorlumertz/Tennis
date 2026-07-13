from html import escape
from typing import Any, TypedDict
import json
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
    button = ""
    if hasExpandableRows:
      button = (
        f"<button class=\"toggle-button\" type=\"button\" data-target=\"{categoryId}\""
        " aria-expanded=\"false\">Ver classificacao completa</button>"
      )

    sections.append(
      f"<section class=\"category-section\" id=\"{categoryId}\">"
      "<div class=\"category-header\">"
      f"<h2>{escape(str(categoryName))}</h2>"
      f"{button}"
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
  chartDataJson = json.dumps(registrations, ensure_ascii=True)
  return (
    "<section class=\"chart-section\">"
    "<div class=\"section-title\">"
    "<h2>Inscritos por etapa</h2>"
    "</div>"
    f"<div class=\"chart\" data-chart='{escape(chartDataJson, quote=True)}'></div>"
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

    .category-section.is-expanded .ranking-row.is-hidden {{
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
      min-width: max-content;
      padding: 10px 4px 0;
    }}

    .chart-column {{
      align-items: center;
      display: flex;
      flex-direction: column;
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
  <script>
    var palette = ['#d8aaa3', '#9bb7c8', '#a8bf9d', '#d6bd86', '#b9a7c8', '#c5b8a8', '#c9988f', '#93aaa4'];
    var toggleButtons = document.querySelectorAll('.toggle-button');

    for (var toggleIndex = 0; toggleIndex < toggleButtons.length; toggleIndex += 1) {{
      toggleButtons[toggleIndex].addEventListener('click', function () {{
        var button = this;
        var section = document.getElementById(button.getAttribute('data-target'));
        var isExpanded = section.classList.toggle('is-expanded');
        button.setAttribute('aria-expanded', String(isExpanded));
        button.textContent = isExpanded ? 'Ver apenas top 5' : 'Ver classificacao completa';
      }});
    }}

    var charts = document.querySelectorAll('.chart');
    for (var chartIndex = 0; chartIndex < charts.length; chartIndex += 1) {{
      var chart = charts[chartIndex];
      var stages = JSON.parse(chart.getAttribute('data-chart') || '[]');
      var categoryNames = [];
      var colorByCategory = {{}};
      var maxTotal = 1;

      for (var stageIndexForSetup = 0; stageIndexForSetup < stages.length; stageIndexForSetup += 1) {{
        var setupStage = stages[stageIndexForSetup];
        if (setupStage.total > maxTotal) {{
          maxTotal = setupStage.total;
        }}

        for (var setupCategoryIndex = 0; setupCategoryIndex < setupStage.categories.length; setupCategoryIndex += 1) {{
          var setupCategoryName = setupStage.categories[setupCategoryIndex].name;
          if (categoryNames.indexOf(setupCategoryName) === -1) {{
            categoryNames.push(setupCategoryName);
            colorByCategory[setupCategoryName] = palette[(categoryNames.length - 1) % palette.length];
          }}
        }}
      }}

      var maxBarHeight = 210;
      var bars = document.createElement('div');
      bars.className = 'chart-bars';

      for (var stageIndex = 0; stageIndex < stages.length; stageIndex += 1) {{
        var stage = stages[stageIndex];
        var column = document.createElement('div');
        column.className = 'chart-column';

        var total = document.createElement('div');
        total.className = 'chart-total';
        total.textContent = stage.total;

        var bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = stage.total > 0 ? ((stage.total / maxTotal) * maxBarHeight) + 'px' : '0';

        var label = document.createElement('div');
        label.className = 'chart-label';
        label.textContent = stage.name;
        label.title = label.textContent;

        for (var categoryIndex = 0; categoryIndex < stage.categories.length; categoryIndex += 1) {{
          var category = stage.categories[categoryIndex];
          var segment = document.createElement('div');
          segment.className = 'bar-segment';
          segment.style.height = stage.total > 0 ? ((category.count / stage.total) * 100) + '%' : '0';
          segment.style.background = colorByCategory[category.name];
          segment.title = category.name + ': ' + category.count;
          segment.textContent = category.count > 0 ? category.count : '';
          bar.appendChild(segment);
        }}

        column.appendChild(total);
        column.appendChild(bar);
        column.appendChild(label);
        bars.appendChild(column);
      }}
      chart.appendChild(bars);

      var legend = document.createElement('div');
      legend.className = 'legend';
      for (var legendIndex = 0; legendIndex < categoryNames.length; legendIndex += 1) {{
        var name = categoryNames[legendIndex];
        var item = document.createElement('span');
        item.className = 'legend-item';

        var swatch = document.createElement('span');
        swatch.className = 'legend-swatch';
        swatch.style.background = colorByCategory[name];

        var text = document.createElement('span');
        text.textContent = name;

        item.appendChild(swatch);
        item.appendChild(text);
        legend.appendChild(item);
      }}
      chart.appendChild(legend);
    }}
  </script>
</body>
</html>
"""
  with open(filePath, "w", encoding="utf-8") as file:
    file.write(html)


if __name__ == '__main__':
  from tennis_manager.fileReader import ReadInputFile
  tournaments = [
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\1aEtapa\RankingDeDuplas2026_1aEtapa_5.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\2aEtapa\RD_2026_2aEtapa_4.txt"),
    ReadInputFile(r"C:\Users\vitor\Desktop\Vitor\Dpto Tenis SOGIPA\2026\Ranking de Duplas\3aEtapa\RD3aEtapa_8.txt"),
  ]
  ranking = Ranking('RankingTest', tournaments, discardWorstValue=False)
  ExportToHtml(ranking, "ranking.html")
