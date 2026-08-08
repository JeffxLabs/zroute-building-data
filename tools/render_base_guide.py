#!/usr/bin/env python3
"""Render the complete Base level 1–30 requirement route as an SVG poster."""

import argparse
import html
import json
import math
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path


WIDTH, HEIGHT = 3300, 2370
COLORS = ("#5ee6a8", "#ffc857", "#ff6b6b")
RESOURCE_NAMES = {1: "food", 2: "metal", 3: "oil"}
SHORT_NAMES = {
    "Alpha Research Division": "Alpha Research",
    "Soldier Training Camp": "Soldier Camp",
    "Warrior Training Center": "Warrior Center",
    "Engineering Department": "Engineering",
}


def compact(value):
    for size, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if value >= size:
            return f"{value / size:.3f}".rstrip("0").rstrip(".") + suffix
    return str(value)


def time_text(seconds, units=4):
    result = []
    for size, suffix in ((86400, "d"), (3600, "h"), (60, "m"), (1, "s")):
        amount, seconds = divmod(seconds, size)
        if amount:
            result.append(f"{amount}{suffix}")
    return " ".join(result[:units]) or "0s"


def summarize(actions):
    result = {"seconds": 0, "food": 0, "metal": 0, "oil": 0}
    for action in actions:
        result["seconds"] += action["base_time_seconds"] or 0
        for cost in action["costs"]:
            if cost["type"] not in RESOURCE_NAMES and cost["count"]:
                raise ValueError(f"unhandled route resource type {cost['type']}")
            if cost["type"] in RESOURCE_NAMES:
                result[RESOURCE_NAMES[cost["type"]]] += cost["count"]
        if action["special_costs"]:
            raise ValueError(f"unhandled special route cost: {action['special_costs']}")
    return result


def build_route(base_document, progression):
    base_rows = base_document["upgrades"]
    buildings = {building["id"]: building for building in progression["buildings"]}
    levels = {building_id: {row["level"]: row for row in building["levels"]} for building_id, building in buildings.items()}
    state = {building_id: building["initial_level"] or 0 for building_id, building in buildings.items()}

    def ensure(building_id, target, current, stack=()):
        if current.get(building_id, 0) >= target:
            return []
        if building_id in stack:
            raise ValueError(f"future-level dependency cycle through building {building_id}")
        actions = []
        while current.get(building_id, 0) < target:
            level = current.get(building_id, 0) + 1
            try:
                row = levels[building_id][level]
            except KeyError as error:
                raise ValueError(f"missing building {building_id} level {level}") from error
            for condition in row["prerequisites"]:
                if condition["kind"] == "building_level":
                    for dependency in condition["building_ids"]:
                        actions += ensure(dependency, condition["minimum_level"], current, stack + (building_id,))
                elif condition["kind"] == "any_building_in_list_level":
                    choices = []
                    for dependency in condition["building_ids"]:
                        trial = current.copy()
                        try:
                            trial_actions = ensure(dependency, condition["minimum_level"], trial, stack + (building_id,))
                        except ValueError:
                            continue
                        trial_total = summarize(trial_actions)
                        choices.append((trial_total["seconds"], sum(trial_total[name] for name in RESOURCE_NAMES.values()), dependency, trial, trial_actions))
                    if not choices:
                        raise ValueError(f"no feasible option for {condition}")
                    _, _, _, chosen_state, chosen_actions = min(choices)
                    current.clear()
                    current.update(chosen_state)
                    actions += chosen_actions
                else:
                    raise ValueError(f"unsupported route condition {condition}")
            previous = current.get(building_id, 0)
            if previous != level - 1:
                raise ValueError(f"non-sequential building {building_id}: {previous} -> {level}")
            current[building_id] = level
            actions.append({"building_id": building_id, "building_name": buildings[building_id]["name"], "from_level": previous, **row})
        return actions

    route, all_actions = [], []
    for expected, base_row in enumerate(base_rows, 1):
        if base_row["target_level"] != expected:
            raise ValueError("Base rows are not sequential")
        actions = ensure(1001, expected, state)
        direct = [action for action in actions if action["building_id"] == 1001]
        prerequisites = [action for action in actions if action["building_id"] != 1001]
        if len(direct) != 1:
            raise ValueError(f"Base {expected} produced {len(direct)} direct actions")
        direct_total = summarize(direct)
        if direct_total["seconds"] != base_row["base_time_seconds"] or any(direct_total[name] != base_row["costs"][name] for name in RESOURCE_NAMES.values()):
            raise ValueError(f"Base {expected} source mismatch")
        grouped = {}
        for action in prerequisites:
            grouped.setdefault(action["building_id"], []).append(action)
        route.append({
            "level": expected,
            "base": direct_total,
            "prerequisites": summarize(prerequisites),
            "building_work": [
                {
                    "name": SHORT_NAMES.get(group[0]["building_name"], group[0]["building_name"]),
                    "from_level": group[0]["from_level"],
                    "to_level": group[-1]["level"],
                    **summarize(group),
                }
                for group in grouped.values()
            ],
            "actions": actions,
        })
        all_actions += actions
    if len(all_actions) != 220:
        raise ValueError(f"unexpected route length: {len(all_actions)} actions")
    return route, summarize(all_actions)


def work_lines(groups):
    lines = []
    for group in groups:
        value = f"{group['name']} {group['from_level']}→{group['to_level']} · {time_text(group['seconds'], 2)}"
        lines += textwrap.wrap(value, width=42, break_long_words=False)
    if len(lines) > 5:
        raise ValueError(f"building-work text exceeds row: {lines}")
    return lines or ["None"]


def text(x, y, value, css="body", anchor=None):
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{css}"{extra}>{html.escape(str(value))}</text>'


def render(base_source, progression_source, output):
    base_document = json.loads(base_source.read_text(encoding="utf-8"))
    progression = json.loads(progression_source.read_text(encoding="utf-8"))
    rows, route_total = build_route(base_document, progression)
    base_total = summarize([action for row in rows for action in row["actions"] if action["building_id"] == 1001])
    max_base_time = max(row["base"]["seconds"] for row in rows)

    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
<title id="title">Z Route complete Base leveling route, levels 1 through 30</title>
<desc id="description">A three-column guide listing Base construction time, combined Base and prerequisite resources, and per-building prerequisite workloads for multi-slot scheduling at every Base level.</desc>
<style>
  .title {{ font: 800 54px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .subtitle {{ font: 400 24px Inter,Segoe UI,sans-serif; fill: #9aa9c3 }}
  .card-label {{ font: 700 17px Inter,Segoe UI,sans-serif; fill: #8ea0bd; letter-spacing: 2px }}
  .card-value {{ font: 800 30px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .card-note {{ font: 400 18px Inter,Segoe UI,sans-serif; fill: #aab7cc }}
  .band {{ font: 800 27px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .column {{ font: 700 14px Inter,Segoe UI,sans-serif; fill: #7789a7; letter-spacing: 1.3px }}
  .level {{ font: 800 24px Inter,Segoe UI,sans-serif; fill: #f5f7ff }}
  .time {{ font: 700 18px Inter,Segoe UI,sans-serif; fill: #dce5f5 }}
  .resource {{ font: 600 15px Inter,Segoe UI,sans-serif; fill: #aebbd0 }}
  .body {{ font: 500 16px Inter,Segoe UI,sans-serif; fill: #d6deec }}
  .none {{ font: italic 500 16px Inter,Segoe UI,sans-serif; fill: #7183a1 }}
  .total-label {{ font: 700 15px Inter,Segoe UI,sans-serif; fill: #8798b5; letter-spacing: 1.2px }}
  .total {{ font: 700 18px Inter,Segoe UI,sans-serif; fill: #dce5f5 }}
  .footer {{ font: 400 17px Inter,Segoe UI,sans-serif; fill: #8798b5 }}
</style>
<rect width="3300" height="2370" fill="#08111f"/>
<circle cx="3050" cy="-70" r="510" fill="#162a47" opacity=".45"/>
<circle cx="80" cy="2370" r="390" fill="#10243d" opacity=".5"/>''']
    svg += [
        text(45, 75, "Z ROUTE  /  COMPLETE BASE LEVELING GUIDE", "title"),
        text(47, 117, "Base time, combined resource requirements, and independently schedulable prerequisite building work", "subtitle"),
    ]

    cards = (
        (45, "DIRECT BASE TIME", time_text(base_total["seconds"]), "Base levels 1–30 · before speed modifiers"),
        (1130, "FULL ROUTE CORE RESOURCES", f"{compact(route_total['food'])} Food  ·  {compact(route_total['metal'])} Metal", f"{compact(route_total['oil'])} Oil, including prerequisites"),
        (2215, "PARALLEL PREREQUISITES", "Per-building times shown", "Elapsed time depends on construction slots and scheduling"),
    )
    for x, label, value, note in cards:
        svg.append(f'<rect x="{x}" y="150" width="1040" height="142" rx="18" fill="#101d31" stroke="#213553"/>')
        svg += [text(x + 28, 185, label, "card-label"), text(x + 28, 232, value, "card-value"), text(x + 28, 266, note, "card-note")]

    row_height, top = 156, 430
    for band_index, start in enumerate((0, 10, 20)):
        x, color = 45 + band_index * 1075, COLORS[band_index]
        group = rows[start:start + 10]
        svg.append(f'<rect x="{x}" y="350" width="1040" height="1820" rx="20" fill="#0d192b" stroke="#213553"/>')
        svg.append(f'<rect x="{x}" y="350" width="1040" height="6" rx="3" fill="{color}"/>')
        svg += [
            text(x + 25, 394, f"BASE LEVELS {start + 1}–{start + 10}", "band"),
            text(x + 25, top, "LV", "column"),
            text(x + 105, top, "BASE TIME", "column"),
            text(x + 330, top, "TOTAL RESOURCES", "column"),
            text(x + 645, top, "BUILDING WORK REQUIRED", "column"),
        ]
        for offset, row in enumerate(group):
            y = top + 18 + offset * row_height
            fill = "#111f34" if offset % 2 == 0 else "#0f1c2f"
            svg.append(f'<g id="level-{row["level"]}"><rect x="{x + 12}" y="{y}" width="1016" height="146" rx="12" fill="{fill}"/>')
            svg.append(f'<rect x="{x + 12}" y="{y}" width="5" height="146" rx="2" fill="{color}" opacity=".8"/>')
            svg.append(text(x + 35, y + 42, f"{row['level']:02d}", "level"))
            svg.append(text(x + 105, y + 29, time_text(row["base"]["seconds"]), "time"))
            bar = 12 + 207 * math.log10(row["base"]["seconds"] + 1) / math.log10(max_base_time + 1)
            svg.append(f'<rect x="{x + 105}" y="{y + 40}" width="220" height="5" rx="2" fill="#263a57"/>')
            svg.append(f'<rect x="{x + 105}" y="{y + 40}" width="{bar:.1f}" height="5" rx="2" fill="{color}"/>')
            total = summarize(row["actions"])
            svg += [
                text(x + 330, y + 29, "Base + requirements", "body"),
                text(x + 330, y + 62, f"F {total['food']:,}", "resource"),
                text(x + 330, y + 86, f"M {total['metal']:,}", "resource"),
                text(x + 330, y + 110, f"O {total['oil']:,}", "resource"),
            ]
            lines = work_lines(row["building_work"])
            for line_index, line in enumerate(lines):
                svg.append(text(x + 645, y + 31 + line_index * 23, line, "none" if line == "None" else "body"))
            svg.append("</g>")

        band_total = summarize([action for row in group for action in row["actions"]])
        y = top + 18 + 10 * row_height + 30
        svg += [
            text(x + 25, y, "BAND TOTAL · BASE TIME + ALL RESOURCES", "total-label"),
            text(x + 25, y + 34, time_text(sum(row["base"]["seconds"] for row in group)), "total"),
            text(x + 380, y + 5, f"F {compact(band_total['food'])}  ·  M {compact(band_total['metal'])}", "total"),
            text(x + 380, y + 38, f"O {compact(band_total['oil'])}", "total"),
        ]

    svg += [
        text(45, 2220, "HOW TO READ", "card-label"),
        text(45, 2254, "Each row is incremental from the prior Base level. Total Resources includes that Base upgrade and every recursively required building upgrade; sum rows for any cumulative target.", "footer"),
        text(45, 2285, "Building Work shows each prerequisite building’s level range and its own sequential time. Different buildings may run in parallel when additional construction slots are available.", "footer"),
        text(45, 2316, "Base Time excludes prerequisite time. Actual elapsed time depends on slot count, scheduling, speed bonuses, alliance help, events, and server overrides. F Food · M Metal · O Oil.", "footer"),
        text(45, 2347, "Source: com.zroute.global v1.30.07 · catalog V202608062022", "footer"),
        text(3255, 2347, "zroute-building-data", "footer", "end"),
        "</svg>",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(svg), encoding="utf-8")
    root = ET.parse(output).getroot()
    assert root.tag.endswith("svg") and all(root.find(f".//*[@id='level-{level}']") is not None for level in range(1, 31))
    assert route_total == {"seconds": 110_094_695, "food": 13_352_203_480, "metal": 12_992_121_750, "oil": 4_500_620_760}
    print(f"ok: rendered complete 220-action Base route to {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_source", type=Path)
    parser.add_argument("progression_source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.base_source, args.progression_source, args.output)


if __name__ == "__main__":
    main()
