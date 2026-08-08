#!/usr/bin/env python3
"""Render the Base level 1–30 requirements as a standalone SVG poster."""

import argparse
import html
import json
import math
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path


WIDTH, HEIGHT = 2400, 2140
COLORS = ("#5ee6a8", "#ffc857", "#ff6b6b")


def compact(value):
    for size, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if value >= size:
            return f"{value / size:.3f}".rstrip("0").rstrip(".") + suffix
    return str(value)


def time_text(seconds):
    result = []
    for size, suffix in ((86400, "d"), (3600, "h"), (60, "m"), (1, "s")):
        amount, seconds = divmod(seconds, size)
        if amount:
            result.append(f"{amount}{suffix}")
    return " ".join(result) or "0s"


def requirement_text(prerequisites):
    parts = []
    for item in prerequisites:
        names = [building["name"] for building in item["buildings"]]
        if item["match"] == "any":
            parts.append(f"Any training center Lv {item['minimum_level']} ({' / '.join(name.replace(' Training Center', '') for name in names)})")
        else:
            parts.append(f"{names[0]} Lv {item['minimum_level']}")
    return " + ".join(parts) or "None"


def text(x, y, value, css="body", anchor=None):
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{css}"{extra}>{html.escape(str(value))}</text>'


def render(source, output):
    document = json.loads(source.read_text(encoding="utf-8"))
    rows = document["upgrades"]
    assert len(rows) == 30 and [row["target_level"] for row in rows] == list(range(1, 31))
    total_time = sum(row["base_time_seconds"] for row in rows)
    totals = {kind: sum(row["costs"][kind] for row in rows) for kind in ("food", "metal", "oil")}
    max_seconds = max(row["base_time_seconds"] for row in rows)

    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
<title id="title">Z Route Base leveling requirements, levels 1 through 30</title>
<desc id="description">A three-column guide listing exact base construction time, Food, Metal, Oil, and building prerequisites for every Base level.</desc>
<style>
  .title {{ font: 800 52px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .subtitle {{ font: 400 23px Inter,Segoe UI,sans-serif; fill: #9aa9c3 }}
  .card-label {{ font: 700 17px Inter,Segoe UI,sans-serif; fill: #8ea0bd; letter-spacing: 2px }}
  .card-value {{ font: 800 31px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .card-note {{ font: 400 18px Inter,Segoe UI,sans-serif; fill: #aab7cc }}
  .band {{ font: 800 27px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .column {{ font: 700 15px Inter,Segoe UI,sans-serif; fill: #7789a7; letter-spacing: 1.4px }}
  .level {{ font: 800 24px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .time {{ font: 700 19px Inter,Segoe UI,sans-serif; fill: #dce5f5 }}
  .resource {{ font: 600 16px Inter,Segoe UI,sans-serif; fill: #aebbd0 }}
  .body {{ font: 500 18px Inter,Segoe UI,sans-serif; fill: #d6deec }}
  .none {{ font: italic 500 18px Inter,Segoe UI,sans-serif; fill: #7183a1 }}
  .total-label {{ font: 700 15px Inter,Segoe UI,sans-serif; fill: #8798b5; letter-spacing: 1.2px }}
  .total {{ font: 700 18px Inter,Segoe UI,sans-serif; fill: #dce5f5 }}
  .footer {{ font: 400 17px Inter,Segoe UI,sans-serif; fill: #8798b5 }}
</style>
<rect width="2400" height="2140" fill="#08111f"/>
<circle cx="2200" cy="-80" r="430" fill="#162a47" opacity=".45"/>
<circle cx="80" cy="2140" r="360" fill="#10243d" opacity=".5"/>''']
    svg += [
        text(45, 72, "Z ROUTE  /  BASE LEVELING GUIDE", "title"),
        text(47, 112, "Requirements and unmodified construction time for every Base level", "subtitle"),
    ]

    cards = (
        (45, "TOTAL BASE TIME", time_text(total_time), "Levels 1–30, sequential"),
        (825, "TOTAL CORE RESOURCES", f"{compact(totals['food'])} Food  ·  {compact(totals['metal'])} Metal", f"{compact(totals['oil'])} Oil"),
        (1605, "DATA SCOPE", "Client v1.30.07", "Before speed bonuses, help, events, or overrides"),
    )
    for x, label, value, note in cards:
        svg.append(f'<rect x="{x}" y="150" width="750" height="142" rx="18" fill="#101d31" stroke="#213553"/>')
        svg += [text(x + 28, 185, label, "card-label"), text(x + 28, 232, value, "card-value"), text(x + 28, 266, note, "card-note")]

    row_height, top = 134, 420
    for band_index, start in enumerate((0, 10, 20)):
        x, color = 45 + band_index * 780, COLORS[band_index]
        group = rows[start:start + 10]
        svg.append(f'<rect x="{x}" y="350" width="750" height="1615" rx="20" fill="#0d192b" stroke="#213553"/>')
        svg.append(f'<rect x="{x}" y="350" width="750" height="6" rx="3" fill="{color}"/>')
        svg += [
            text(x + 25, 394, f"BASE LEVELS {start + 1}–{start + 10}", "band"),
            text(x + 25, top, "LEVEL", "column"),
            text(x + 118, top, "TIME + RESOURCES", "column"),
            text(x + 370, top, "REQUIREMENTS", "column"),
        ]
        for offset, row in enumerate(group):
            y = top + 18 + offset * row_height
            fill = "#111f34" if offset % 2 == 0 else "#0f1c2f"
            svg.append(f'<g id="level-{row["target_level"]}"><rect x="{x + 12}" y="{y}" width="726" height="124" rx="12" fill="{fill}"/>')
            svg.append(f'<rect x="{x + 12}" y="{y}" width="5" height="124" rx="2" fill="{color}" opacity=".8"/>')
            svg += [
                text(x + 37, y + 43, f"{row['target_level']:02d}", "level"),
                text(x + 118, y + 35, row["base_time_human"], "time"),
            ]
            bar = 10 + 205 * math.log10(max(row["base_time_seconds"], 2) / 2 + 1) / math.log10(max_seconds / 2 + 1)
            svg.append(f'<rect x="{x + 118}" y="{y + 48}" width="215" height="6" rx="3" fill="#263a57"/>')
            svg.append(f'<rect x="{x + 118}" y="{y + 48}" width="{bar:.1f}" height="6" rx="3" fill="{color}"/>')
            costs = row["costs"]
            svg += [
                text(x + 118, y + 80, f"F {costs['food']:,}  ·  M {costs['metal']:,}", "resource"),
                text(x + 118, y + 105, f"O {costs['oil']:,}", "resource"),
            ]
            requirement = requirement_text(row["prerequisites"])
            for line_index, line in enumerate(textwrap.wrap(requirement, width=39, break_long_words=False) or ["None"]):
                svg.append(text(x + 370, y + 38 + line_index * 24, line, "none" if requirement == "None" else "body"))
            svg.append("</g>")

        band_time = sum(row["base_time_seconds"] for row in group)
        band_totals = {kind: sum(row["costs"][kind] for row in group) for kind in totals}
        y = top + 18 + 10 * row_height + 30
        svg += [
            text(x + 25, y, "BAND TOTAL", "total-label"),
            text(x + 25, y + 32, time_text(band_time), "total"),
            text(x + 215, y + 5, f"F {compact(band_totals['food'])}  ·  M {compact(band_totals['metal'])}", "total"),
            text(x + 215, y + 37, f"O {compact(band_totals['oil'])}", "total"),
        ]

    svg += [
        text(45, 2025, "HOW TO READ", "card-label"),
        text(45, 2059, "Each row is the target Base level. All listed requirements must be met; “Any training center” means one of Warrior, Assault, or Tactical.", "footer"),
        text(45, 2090, f"Times and costs are client base values. Total time: {time_text(total_time)}. Data source: com.zroute.global · catalog V202608062022.", "footer"),
        text(2355, 2090, "zroute-building-data", "footer", "end"),
        "</svg>",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(svg), encoding="utf-8")
    root = ET.parse(output).getroot()
    assert root.tag.endswith("svg") and all(root.find(f".//*[@id='level-{level}']") is not None for level in range(1, 31))
    print(f"ok: rendered 30 Base levels to {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.source, args.output)


if __name__ == "__main__":
    main()
