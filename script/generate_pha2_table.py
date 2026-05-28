#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime
import random
import statistics
from pathlib import Path


ROBOTS = [f"robot-{index:02d}" for index in range(1, 7)]
COLORS = ["#1f77b4", "#17becf", "#ff7f0e", "#9467bd", "#e377c2", "#2ca02c"]


def random_row(robot: str) -> dict[str, float | str]:
    return {
        "robot": robot,
        "score": round(random.uniform(0, 100), 2),
        "beta1_p": round(random.uniform(0, 1), 4),
        "delta30d1": round(random.uniform(-10, 10), 3),
        "beta1": round(random.uniform(-2, 2), 4),
        "delta2m1m": round(random.uniform(-15, 15), 3),
    }


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def series_from_rows(rows: list[dict[str, float | str]]) -> dict[str, list[float]]:
    trends: dict[str, list[float]] = {}
    for row in rows:
        base = 30 + float(row["score"]) / 8
        trends[str(row["robot"])] = [round(base + random.uniform(-1.8, 1.8), 2) for _ in range(8)]
    return trends


def render_chart_svg(trends: dict[str, list[float]]) -> str:
    all_values = [value for values in trends.values() for value in values]
    minimum, maximum = min(all_values) - 1, max(all_values) + 1
    x_count = len(next(iter(trends.values())))
    width, height = 860, 300
    inner_w, inner_h = width - 50, height - 30

    def map_x(index: int) -> float:
        return 25 + index * (inner_w / (x_count - 1))

    def map_y(value: float) -> float:
        return 15 + (maximum - value) * (inner_h / (maximum - minimum))

    lines = []
    labels = []
    for i, (robot, values) in enumerate(trends.items()):
        points = " ".join(f"{map_x(index):.2f},{map_y(value):.2f}" for index, value in enumerate(values))
        color = COLORS[i % len(COLORS)]
        lines.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.2" opacity="0.95"/>'
        )
        labels.append(f'<span><i style="background:{color}"></i>{robot}</span>')

    return (
        f"""<div class="legend">{''.join(labels)}</div>
<svg viewBox="0 0 {width} {height}" role="img" aria-label="PHA2 trend chart">
  <line x1="25" y1="15" x2="25" y2="{height-15}" stroke="#6d6d6d" stroke-width="1"/>
  <line x1="25" y1="{height-15}" x2="{width-15}" y2="{height-15}" stroke="#6d6d6d" stroke-width="1"/>
  {''.join(lines)}
</svg>"""
    )


def render_html(rows: list[dict[str, float | str]]) -> str:
    ranked = sorted(rows, key=lambda row: float(row["score"]), reverse=True)
    trends = series_from_rows(ranked)
    trend_values = [value for values in trends.values() for value in values]
    median = statistics.median(trend_values)
    std = statistics.pstdev(trend_values)
    maximum = max(trend_values)
    minimum = min(trend_values)
    chart = render_chart_svg(trends)
    updated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    table_rows = "\n".join(
        (
            "<tr>"
            f"<td>{row['robot'].upper()}</td>"
            f"<td class='score'>{fmt(float(row['score']))}</td>"
            f"<td>{fmt(float(row['beta1_p']) * 100)}%</td>"
            f"<td class='delta'>{fmt(float(row['delta30d1']), 1)}%</td>"
            f"<td>{fmt(float(row['beta1']))}</td>"
            f"<td class='delta'>{fmt(float(row['delta2m1m']), 1)}%</td>"
            "</tr>"
        )
        for row in ranked
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TRENDING PHA2 (Mock)</title>
  <style>
    :root {{ --blue:#101e78; --deep:#132569; --bg:#ececec; --card:#ffffff; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family: "Segoe UI", Arial, sans-serif; background:var(--bg); color:#303030; }}
    .layout {{ display:grid; grid-template-columns:220px 1fr; min-height:100vh; }}
    .sidebar {{
      background:linear-gradient(180deg,#1a2f86,#0c1b59); color:#d8e2ff; padding:1.2rem 1rem;
      display:flex; flex-direction:column; gap:0.9rem;
    }}
    .brand {{ font-size:1.8rem; font-weight:700; letter-spacing:.08em; margin-bottom:1rem; }}
    .filter {{ border:1px solid #4762be; padding:.55rem .65rem; border-radius:6px; color:#d8e2ff; }}
    .content {{ padding:1.2rem; display:grid; grid-template-rows:auto 1fr auto auto; gap:1rem; }}
    .topbar {{ display:flex; align-items:center; justify-content:space-between; }}
    .title {{ font-size:3rem; font-weight:900; color:var(--blue); letter-spacing:.02em; }}
    .title span {{ font-weight:400; }}
    .dash-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:1rem; min-height:540px; }}
    .panel {{ background:var(--card); border:1px solid #d0d4e0; border-radius:8px; overflow:hidden; }}
    .panel-title {{ background:var(--blue); color:#fff; padding:.7rem .9rem; font-size:1.55rem; font-weight:700; }}
    .panel-body {{ padding:.9rem; }}
    .legend {{ display:flex; flex-wrap:wrap; gap:.8rem; margin-bottom:.6rem; font-size:.9rem; }}
    .legend span {{ display:flex; align-items:center; gap:.35rem; }}
    .legend i {{ width:.7rem; height:.7rem; border-radius:50%; display:inline-block; }}
    svg {{ width:100%; height:auto; background:#fbfbfb; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; font-size:1.65rem; }}
    th {{ text-align:left; padding:.5rem .45rem; color:#4e4e4e; border-bottom:2px solid #c5c5c5; }}
    td {{ padding:.45rem; border-bottom:1px solid #ececec; }}
    td:not(:first-child), th:not(:first-child) {{ text-align:right; }}
    td.score {{ background:linear-gradient(90deg,#9f0000,#d32f2f); color:#fff; font-weight:700; }}
    td.delta {{ background:linear-gradient(90deg,#eaf8ea,#d7f0d7); }}
    .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; }}
    .card {{ background:var(--card); border:1px solid #d4d9e5; border-radius:8px; text-align:center; padding:1.5rem .8rem; }}
    .card .v {{ font-size:3rem; font-weight:800; color:#1d2f80; }}
    .card .l {{ margin-top:.35rem; font-size:1.2rem; color:#555; }}
    .footer {{ text-align:right; font-size:.95rem; color:#333; }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">STELLANTIS</div>
      <div class="filter">HOME</div>
      <div class="filter">ANO: Todos</div>
      <div class="filter">MÊS: Todos</div>
      <div class="filter">SEMANA: Todos</div>
      <div class="filter">ROBÔ: Todos</div>
      <div class="filter">LINHA: Todos</div>
      <div class="filter">STATUS: Todos</div>
    </aside>
    <main class="content">
      <div class="topbar">
        <div class="title">TRENDING <span>PHA2</span></div>
        <div style="font-size:4.2rem; font-weight:800; color:#4d4d4d;">Jeep</div>
      </div>
      <div class="dash-grid">
        <section class="panel">
          <div class="panel-title">Média de pha2 por Ano, Mês e Dia</div>
          <div class="panel-body">{chart}</div>
        </section>
        <section class="panel">
          <div class="panel-title">MÉDIA PHA2 POR MÁQUINAS</div>
          <div class="panel-body">
            <table>
              <thead>
                <tr><th>ROBÔ</th><th>Score</th><th>β1_p</th><th>Δ 30D|1D</th><th>β1</th><th>Δ 2M|1M</th></tr>
              </thead>
              <tbody>
{table_rows}
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <div class="cards">
        <div class="card"><div class="v">{fmt(median)}</div><div class="l">Mediana de pha2</div></div>
        <div class="card"><div class="v">{fmt(std)}</div><div class="l">Desvio padrão de pha2</div></div>
        <div class="card"><div class="v">{fmt(maximum)}</div><div class="l">Máximo de pha2</div></div>
        <div class="card"><div class="v">{fmt(minimum)}</div><div class="l">Mínimo de pha2</div></div>
      </div>
      <div class="footer"><strong>ATUALIZAÇÃO:</strong> {updated_at}</div>
    </main>
  </div>
</body>
</html>
"""


def main() -> None:
    rows = [random_row(robot) for robot in ROBOTS]
    output_path = Path(__file__).resolve().parent.parent / "index.html"
    output_path.write_text(render_html(rows), encoding="utf-8")
    print(f"Updated {output_path}")


if __name__ == "__main__":
    main()
