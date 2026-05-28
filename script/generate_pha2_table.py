#!/usr/bin/env python3

from __future__ import annotations

import random
from pathlib import Path


ROBOTS = [f"robot-{index:02d}" for index in range(1, 7)]


def random_row(robot: str) -> dict[str, float | str]:
    return {
        "robot": robot,
        "score": round(random.uniform(0, 100), 2),
        "beta1_p": round(random.uniform(0, 1), 4),
        "delta30d1": round(random.uniform(-10, 10), 3),
        "beta1": round(random.uniform(-2, 2), 4),
        "delta2m1m": round(random.uniform(-15, 15), 3),
    }


def render_html(rows: list[dict[str, float | str]]) -> str:
    headers = ["robot", "score", "beta1_p", "delta30d1", "beta1", "delta2m1m"]
    body = "\n".join(
        "<tr>" + "".join(f"<td>{row[column]}</td>" for column in headers) + "</tr>" for row in rows
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PHA2 Robot Score (Mock)</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; min-width: 720px; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem 0.75rem; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    thead {{ background: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>PHA2 Score by Robot (POC)</h1>
  <table>
    <thead>
      <tr>{"".join(f"<th>{header}</th>" for header in headers)}</tr>
    </thead>
    <tbody>
{body}
    </tbody>
  </table>
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
