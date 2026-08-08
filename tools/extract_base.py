#!/usr/bin/env python3
"""Generate the Z Route v1.30.07 Base upgrade dataset from local plaintext tables."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


BUILDING_ID = 1001
EXPECTED_HASHES = {
    "Building.lua": "626e8c94253acbc3d62e35a48995c1672224ae41ef77b16d2ef82a94e73ae9a8",
    "BuildingLevel.lua": "c011f412e2d8b3de100df0c4dd7605718950b30729adee240a9746a2f42208d9",
    "BuildingUpgrade.lua": "ec2855a231be5bc764f831c13abf44fc4814f6c04f53a040e2448856b95668ba",
}
ROW = re.compile(r"^\s*\[(\d+)\] = \{(.*)\},?\s*$")
CONDITION = re.compile(
    r'\{id=(\d+), param1="([^"]*)", param2="([^"]*)", '
    r'param3="([^"]*)", param4="([^"]*)"\}'
)
RESOURCE = re.compile(r'\{type=(\d+), id="[^"]*", count=(\d+)\}')


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_top_level(value):
    parts, start, depth, quoted, escaped = [], 0, 0, False, False
    for index, char in enumerate(value):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    if quoted or depth:
        raise ValueError("unbalanced Lua row")
    parts.append(value[start:].strip())
    return parts


def rows(path):
    parsed = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if match:
            parsed[int(match.group(1))] = split_top_level(match.group(2))
    return parsed


def lua_string(value):
    return None if value == "_" else json.loads(value)


def human_time(seconds):
    units = ((86400, "d"), (3600, "h"), (60, "m"), (1, "s"))
    parts = []
    for size, suffix in units:
        count, seconds = divmod(seconds, size)
        if count:
            parts.append(f"{count}{suffix}")
    return " ".join(parts) or "0s"


def load_names(buildings, lang_path):
    localized = {
        item["id"]: item["en"]
        for item in json.loads(lang_path.read_text(encoding="utf-8"))["datas"]
    }
    result = {}
    for building_id, fields in buildings.items():
        key = lua_string(fields[3])
        result[building_id] = localized.get(key, key or f"Building {building_id}")
    return result


def parse_prerequisites(value, names):
    prerequisites = []
    matches = CONDITION.findall(value)
    if len(matches) != value.count("{id="):
        raise ValueError(f"unparsed prerequisite: {value}")
    for condition_id, param1, param2, _, _ in matches:
        condition_id = int(condition_id)
        if condition_id not in (20103, 20105):
            raise ValueError(f"unknown prerequisite condition {condition_id}")
        building_ids = [int(item) for item in param1.split(";")]
        if any(item not in names or names[item].startswith("buildingname_") for item in building_ids):
            raise ValueError(f"missing prerequisite localization for {building_ids}")
        prerequisites.append(
            {
                "condition_id": condition_id,
                "match": "any" if condition_id == 20105 else "all",
                "buildings": [
                    {"id": item, "name": names.get(item, f"Building {item}")}
                    for item in building_ids
                ],
                "minimum_level": int(param2),
            }
        )
    return prerequisites


def prerequisite_text(prerequisites):
    rendered = []
    for item in prerequisites:
        names = " / ".join(building["name"] for building in item["buildings"])
        prefix = "Any one of " if item["match"] == "any" else ""
        rendered.append(f"{prefix}{names} Lv. {item['minimum_level']}")
    return " AND ".join(rendered)


def build(source_dir, lang_path, out_dir):
    paths = {name: source_dir / name for name in EXPECTED_HASHES}
    actual_hashes = {name: sha256(path) for name, path in paths.items()}
    if actual_hashes != EXPECTED_HASHES:
        raise ValueError(f"unexpected table hashes: {actual_hashes}")

    buildings = rows(paths["Building.lua"])
    levels = rows(paths["BuildingLevel.lua"])
    upgrades = rows(paths["BuildingUpgrade.lua"])
    names = load_names(buildings, lang_path)
    max_level = int(buildings[BUILDING_ID][51])
    expected_levels = list(range(1, max_level + 1))
    level_rows = {
        int(fields[2]): (row_id, fields)
        for row_id, fields in levels.items()
        if int(fields[1]) == BUILDING_ID and int(fields[2]) > 0
    }
    if sorted(level_rows) != expected_levels:
        raise ValueError("Base level rows do not match configured maxLv")

    records = []
    for target_level in expected_levels:
        row_id, level = level_rows[target_level]
        upgrade = upgrades[row_id]
        if upgrade[3] != "{}":
            raise ValueError(f"unexpected special cost at level {target_level}")
        resource_counts = {int(kind): int(count) for kind, count in RESOURCE.findall(upgrade[2])}
        if set(resource_counts) != {1, 2, 3}:
            raise ValueError(f"unexpected resource costs at level {target_level}")
        prerequisites = parse_prerequisites(level[5], names)
        records.append(
            {
                "target_level": target_level,
                "base_time_seconds": int(upgrade[1]),
                "base_time_human": human_time(int(upgrade[1])),
                "costs": {
                    "food": resource_counts.get(1, 0),
                    "metal": resource_counts.get(2, 0),
                    "oil": resource_counts.get(3, 0),
                },
                "prerequisites": prerequisites,
            }
        )

    document = {
        "source": {
            "package": "com.zroute.global",
            "app_version": "1.30.07",
            "catalog_version": "V202608062022",
            "client_build_time": "2026-08-06 20:26:03",
            "table_plaintext_sha256": actual_hashes,
            "localization_plaintext_sha256": sha256(lang_path),
        },
        "building": {"id": BUILDING_ID, "name": names[BUILDING_ID], "max_level": max_level},
        "resource_types": {"1": "Food", "2": "Metal", "3": "Oil"},
        "upgrades": records,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "base-upgrades.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (out_dir / "base-upgrades.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(
            ("target_level", "base_time_seconds", "base_time_human", "food", "metal", "oil", "prerequisites")
        )
        for record in records:
            costs = record["costs"]
            writer.writerow(
                (
                    record["target_level"],
                    record["base_time_seconds"],
                    record["base_time_human"],
                    costs["food"],
                    costs["metal"],
                    costs["oil"],
                    prerequisite_text(record["prerequisites"]),
                )
            )


def check(out_dir):
    document = json.loads((out_dir / "base-upgrades.json").read_text(encoding="utf-8"))
    with (out_dir / "base-upgrades.csv").open(encoding="utf-8", newline="") as source:
        csv_rows = list(csv.DictReader(source))
    upgrades = document["upgrades"]
    assert document["building"] == {"id": 1001, "name": "Base", "max_level": 30}
    assert [row["target_level"] for row in upgrades] == list(range(1, 31))
    assert [int(row["target_level"]) for row in csv_rows] == list(range(1, 31))
    assert all(row["base_time_seconds"] >= 0 and min(row["costs"].values()) >= 0 for row in upgrades)
    assert upgrades[0]["base_time_seconds"] == 2 and upgrades[-1]["base_time_seconds"] == 8_778_637
    assert all(building["name"] for row in upgrades for item in row["prerequisites"] for building in item["buildings"])
    print("ok: 30 Base upgrade rows")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("build")
    generate.add_argument("source_dir", type=Path)
    generate.add_argument("lang_json", type=Path)
    generate.add_argument("out_dir", type=Path)
    verify = commands.add_parser("check")
    verify.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(args.source_dir, args.lang_json, args.out_dir)
        check(args.out_dir)
    else:
        check(args.out_dir)


if __name__ == "__main__":
    main()
