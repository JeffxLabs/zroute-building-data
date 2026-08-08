#!/usr/bin/env python3
"""Build a compact progression model from Z Route v1.30.07 plaintext tables."""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from extract_base import check as check_base
from extract_base import sha256, split_top_level


SOURCES = {
    "Building": ("0eb19f215674df0a721e8af4b6e38b27", "626e8c94253acbc3d62e35a48995c1672224ae41ef77b16d2ef82a94e73ae9a8"),
    "BuildingLevel": ("fe3de944af769d3aed3c085028a01388", "c011f412e2d8b3de100df0c4dd7605718950b30729adee240a9746a2f42208d9"),
    "BuildingUpgrade": ("867eafd983c72fabb00169f6995b94ed", "ec2855a231be5bc764f831c13abf44fc4814f6c04f53a040e2448856b95668ba"),
    "BuildingCountLimit": ("7c25bd166199f36643c1041952586c84", "2c6b439c7f605e0970fa314f14b70c796febfcf6bad26ee57b59c789c6037709"),
    "DefineBenefit": ("358872978fa5d6ea71cc3278941ba487", "3778da5a3a5e623205f5cde728104d50a8c259ef203e5546025c8d7fe4d4d461"),
    "CollegeTech": ("ca0eae5e4286e93f999b6e8907b47848", "eb0e37e4607d3a7b14affa02c1ce6b1b2901c9e9197fcdf9d72e2912ac5d72dd"),
    "CollegeTechLevel": ("97dd856dc66a18e377f248ccbe94279d", "49b8322d773f80039bf671f2ea8bfeb8c6c30ad293e32644644e3d99defbe922"),
    "CollegeTechType": ("dfff5d9d7248a7e30dabfe4216e3d53d", "ecdc96ec072311f52e1453e3ab43e3831c083a393138e51c1efc8cac67abdbfa"),
    "VipPrivilege": ("557146594caa9ac60a1eb7fa8b53ee1f", "99bfc9ed88d0f3ffaa14807c8302f4b947d4a3b64ed4b6444ae3ec920971383c"),
    "ResourceInfo": ("c5d9304dab5e8c3e4453db1b3893a33a", "fc2f809074501b16e4f1398d057fdd14537e87cbd54c7b778806975a80838510"),
    "ResourceSearch": ("8246abd36bcf6cc0676c32ca8ebc0bd8", "3a8e0d4dda967e644d7e33aba6bf30ca96c8ecc2868c4d5c621bf631ae88148c"),
    "Item": ("e8dc564c60c6da1a81c81e37f6d4f280", "f468c2851ed4df7b47805865623587ef408251b4f3a7a6096203934945abe1eb"),
    "HeroInfo": ("b65185a6afa3b72d0e0a0df03f573359", "f88db0f3be6651eb99374c0401564984f2950bdaaa991ffe0c1c6db841317a2a"),
    "HeroLevel": ("d43f6e1ad030a0e87c47d3ce9be66afd", "dc2b14f759e1565267cf47db95a2c102aa451a87af595eaac490431c84e42f88"),
    "HeroStar": ("3559a71b32ce86343518537a0dc09ae4", "7489d811997332db8259c87b8b6a8b68fb4081b4f0bd880de8c298446150b97a"),
    "NewHeroSkill": ("82fa7b3ef945483bf6fa49d1514221af", "1139271080d135aef30323561aa2b77f5fe23ff3124cb6fc23553216d14cb00b"),
    "NewHeroSkillLevel": ("e8ee42e676aac80f1602da0659b796c7", "1647a1c9f093bf0e48b1c5c5decc9bfef63cbf43913ffd60d075f48c547f5d72"),
    "HeroExclusive": ("c6633163250278a05ba21285711dd313", "80bd5f755ce606a971107a8ad0c51a97f067c65d09dbb19402e1a0ed2912a128"),
    "HeroExclusiveGearLevel": ("c521dbbe20397444b599cac16cde1dfb", "d0b58344caf455e83bd0483bb61f1319ac9ec081cc3098986a1e43d305fd1e16"),
    "HeroExclusiveGearStrengthen": ("7ed748f1a65f0de871e363df1b506418", "3c0ff02cea3f7d7f0afcd6c75810fadefc87f3a7413fb6a347c72fa407c51d23"),
    "EquipmentBase": ("4f27bbaae33b1e27f2f3d027f12be7fc", "8001b24bbe4e39b1db85d5297360b161ce6ad951cba71e97e6d399090576ca7c"),
    "EquipmentStrengthen": ("f55e78d377d3fe887ef3380310b78a3e", "8ea442a0d0d6e817d457c4f1c65883515b51f4e76c64e0090921e35308c52421"),
    "EquipmentPromotion": ("7243e13574084f2f4cfcbb51827cee00", "e652a592060f386121ebd6c94b6d744da8b4734aefe53da7e3f0dffd80a5c30b"),
}
LANG_HASHES = {
    "lang_base.json": "2ca5ca25d6b4da15c10fdbadea57b5b07744fb78261c436df47ab36c92742eb7",
    "lang_benefit.json": "3ca8ef1e57431bc4f7e0b50c47690d223bd7fd811526bc4c6841df69aeda1b64",
    "lang_building.json": "a2d6dc3657aaf825a5a163b0fac769bad78d212e1ffcd41ebda3d64291f0bc82",
    "lang_hero.json": "2281040c8e5c3e390624ad54ced5a82631053ce25b8ceb2f330f01e1e109ff7e",
    "lang_item.json": "7e7eb7bec2d9aea05e90d82deb05399134bebad1b5d1f65af810815c2ac3a053",
}
ROW = re.compile(r'^\s*\[(?:"([^"]+)"|(\d+))\] = \{(.*)\},?\s*$')
KEYS = re.compile(r"\.keys2Index = \{(.*)\}")
RESOURCE = re.compile(r'\{type=(\d+), id="([^"]*)", count="?(-?[\d.]+)"?\}')
BENEFIT = re.compile(r"\{Source=(\d+), Type=(\d+), Value=(-?[\d.eE+]+)\}")
CONDITION = re.compile(r"\{id=\d+,[^{}]*\}")
FIELD = re.compile(r'(\w+)=("(?:\\.|[^"])*"|true|false|-?[\d.]+)')

RESOURCE_TYPES = {
    1: "Food", 2: "Metal", 3: "Oil", 5: "Hero EXP", 11: "Diamond", 99: "Item",
    209: "Profession EXP", 211: "Uranium", 212: "Antibody",
}
CONDITION_TYPES = {
    100004: "open_server_day", 20101: "building_count", 20103: "building_level",
    20104: "building_level_and_count", 20105: "any_building_in_list_level",
    20107: "any_building_class_level", 20201: "research_level",
    300001: "season_stage_day", 300007: "world_season_stage_day",
    400008: "season_task_complete", 80029: "monopoly_event",
    80035: "monopoly_area_unlock",
}
STATIC_CONDITION_KINDS = {"building_level", "any_building_in_list_level", "any_building_class_level", "research_level"}


def atom(value):
    if value in ("_", ""):
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"'):
        return json.loads(value)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?[\d.]+(?:[eE][+-]?\d+)?", value):
        return float(value)
    return value


def number(value):
    result = atom(value)
    return result if isinstance(result, (int, float)) and not isinstance(result, bool) else None


def integer_list(value):
    return [int(item) for item in re.findall(r"-?\d+", value)]


def load_table(path):
    text = path.read_text(encoding="utf-8")
    header = KEYS.search(text)
    if not header:
        raise ValueError(f"missing keys2Index in {path.name}")
    fields = [name for name, _ in sorted(re.findall(r"(\w+)=(\d+)", header.group(1)), key=lambda item: int(item[1]))]
    result = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        key = match.group(1) or int(match.group(2))
        values = split_top_level(match.group(3))
        if len(values) != len(fields):
            raise ValueError(f"{path.name} row {key}: {len(values)} values for {len(fields)} fields")
        result[key] = dict(zip(fields, values))
    return result


def load_localization(source_dir):
    localized = {}
    for filename, expected in LANG_HASHES.items():
        path = source_dir / filename
        if sha256(path) != expected:
            raise ValueError(f"unexpected hash for {filename}")
        localized.update({row["id"]: row["en"] for row in json.loads(path.read_text(encoding="utf-8"))["datas"]})
    return localized


def localized(value, names):
    key = atom(value)
    return names.get(key, key)


def parse_resources(value, names):
    matches = RESOURCE.findall(value)
    if len(matches) != value.count("{type="):
        raise ValueError(f"unparsed resource list: {value}")
    result = []
    for kind, item_id, count in matches:
        kind = int(kind)
        entry = {"type": kind, "type_name": RESOURCE_TYPES.get(kind), "count": atom(count)}
        if item_id:
            entry["item_id"] = item_id
            entry["item_name"] = names.get(item_id, item_id)
        result.append(entry)
    return result


def parse_benefits(value, benefit_names):
    matches = BENEFIT.findall(value)
    if len(matches) != value.count("{Source="):
        raise ValueError(f"unparsed benefit list: {value}")
    return [
        {"source": int(source), "type": int(kind), "name": benefit_names.get(int(kind)), "value": atom(amount)}
        for source, kind, amount in matches
    ]


def parse_conditions(value):
    conditions = []
    for raw in CONDITION.findall(value):
        parsed = {key: atom(item) for key, item in FIELD.findall(raw)}
        parsed["kind"] = CONDITION_TYPES.get(parsed["id"], "unmapped")
        if parsed["kind"] in ("building_level", "any_building_in_list_level"):
            parsed["building_ids"] = [int(item) for item in parsed["param1"].split(";")]
            parsed["minimum_level"] = int(parsed["param2"])
        elif parsed["kind"] == "any_building_class_level":
            parsed["building_class"] = int(parsed["param1"])
            parsed["minimum_level"] = int(parsed["param2"])
        elif parsed["kind"] == "research_level":
            parsed["research_id"] = int(parsed["param1"])
            parsed["minimum_level"] = int(parsed["param2"])
        conditions.append(parsed)
    if len(conditions) != value.count("{id="):
        raise ValueError(f"unparsed condition list: {value}")
    return conditions


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_progression(tables, names, benefit_names):
    buildings = tables["Building"]
    levels = defaultdict(list)
    for row_id, row in tables["BuildingLevel"].items():
        levels[number(row["buildingId"])].append((row_id, row))
    limits = defaultdict(list)
    for row in tables["BuildingCountLimit"].values():
        limits[number(row["buildingId"])].append({
            "base_level": number(row["lockCastleLevel"]), "count": number(row["count"]),
        })
    building_records = []
    for building_id, row in sorted(buildings.items()):
        show_conditions = parse_conditions(row["showCondition"])
        parent_requires_external_state = any(item["kind"] not in STATIC_CONDITION_KINDS for item in show_conditions)
        level_records = []
        for row_id, level in sorted(levels[building_id], key=lambda item: number(item[1]["level"])):
            if number(level["level"]) == 0:
                continue
            upgrade = tables["BuildingUpgrade"].get(row_id)
            prerequisites = parse_conditions(level["precondition"])
            requires_external_state = parent_requires_external_state or any(item["kind"] not in STATIC_CONDITION_KINDS for item in prerequisites)
            level_records.append({
                "level": number(level["level"]),
                "ability": number(level["ability"]),
                "ability_2": number(level["ability2"]),
                "prerequisites": prerequisites,
                "base_time_seconds": number(upgrade["time"]) if upgrade else None,
                "costs": parse_resources(upgrade["cost"], names) if upgrade else [],
                "special_costs": parse_resources(upgrade["specialCost"], names) if upgrade else [],
                "client_reward": parse_resources(upgrade["reward"], names) if upgrade else [],
                "static_optimizer_supported": upgrade is not None and not requires_external_state,
                "requires_external_state": requires_external_state,
            })
        configured_max = number(row["maxLv"])
        available_levels = [item["level"] for item in level_records]
        building_records.append({
            "id": building_id,
            "name": localized(row["name"], names),
            "class": number(row["classify"]),
            "type": number(row["type"]),
            "place_type": number(row["placeType"]),
            "initial_level": number(row["initLevel"]),
            "max_level": configured_max,
            "available_max_level": max(available_levels, default=number(row["initLevel"])),
            "level_rows_complete": available_levels == list(range(1, configured_max + 1)) if configured_max else not available_levels,
            "show_conditions": show_conditions,
            "count_limits": sorted(limits[building_id], key=lambda item: item["base_level"]),
            "levels": level_records,
        })

    tech_types = {
        key: {
            "id": key, "name": localized(row["name"], names),
            "display_conditions": parse_conditions(row["displayCondition"]),
            "prerequisites": parse_conditions(row["precondition"]),
        }
        for key, row in sorted(tables["CollegeTechType"].items())
    }
    tech_levels = defaultdict(list)
    for row in tables["CollegeTechLevel"].values():
        tech_levels[number(row["techId"])].append({
            "level": number(row["level"]),
            "base_time_seconds": number(row["upgradeTime"]),
            "ability": number(row["ability"]),
            "prerequisites": parse_conditions(row["precondition"]),
            "costs": parse_resources(row["cost"], names),
            "special_costs": parse_resources(row["specialCost"], names),
            "benefits": parse_benefits(row["benefit"], benefit_names),
        })
    tech_records = []
    for tech_id, row in sorted(tables["CollegeTech"].items()):
        type_id = number(row["techType"])
        inherited_conditions = tech_types[type_id]["display_conditions"] + tech_types[type_id]["prerequisites"]
        tech_conditions = parse_conditions(row["precondition"])
        inherited_requires_external_state = any(item["kind"] not in STATIC_CONDITION_KINDS for item in inherited_conditions + tech_conditions)
        levels_for_tech = sorted(tech_levels[tech_id], key=lambda item: item["level"])
        for level in levels_for_tech:
            requires_external_state = inherited_requires_external_state or any(item["kind"] not in STATIC_CONDITION_KINDS for item in level["prerequisites"])
            level["static_optimizer_supported"] = not requires_external_state
            level["requires_external_state"] = requires_external_state
        tech_records.append({
            "id": tech_id,
            "name": localized(row["name"], names),
            "type_id": type_id,
            "max_level": number(row["maxLevel"]),
            "max_value": number(row["maxValue"]),
            "prerequisites": tech_conditions,
            "levels": levels_for_tech,
        })
    benefits = []
    for benefit_id, row in sorted(tables["DefineBenefit"].items()):
        benefits.append({
            "id": benefit_id,
            "name": localized(row["name"], names),
            "parameter_type": number(row["paramType"]),
            "display_factor": number(row["displayFactor"]),
            "power_factor": number(row["powerFactor"]),
            "classification": number(row["classify"]),
        })
    vip_speed = tables["VipPrivilege"][8]
    return {
        "buildings": building_records,
        "research_types": list(tech_types.values()),
        "research": tech_records,
        "benefits": benefits,
        "construction_modifiers": {
            "vip_building_speed_percent_by_level": [0] + [number(vip_speed[f"vip{level}"]) or 0 for level in range(1, 19)],
            "research_building_speed_benefit_type": 20005,
            "free_building_speedup_time_benefit_type": 20006,
            "planner_interpretation": {
                "building_speed_stacking": "additive",
                "time_formula": "max(0, ceil(base_time_seconds / (1 + total_building_speed_percent / 100) - free_finish_seconds))",
            },
        },
    }


def build_resources(tables, names, building_names):
    nodes = [{
        "id": key,
        "type": number(row["type"]),
        "type_name": RESOURCE_TYPES.get(number(row["type"]), f"Unmapped client type {number(row['type'])}"),
        "name_key": atom(row["name"]),
        "name": localized(row["name"], names),
        "level": number(row["level"]),
        "required_base_level": number(row["castleLevel"]),
        "amount": number(row["amount"]),
        "speed_value": number(row["speed"]),
        "auto_refresh": atom(row["autoRefresh"]),
    } for key, row in sorted(tables["ResourceInfo"].items())]
    searches = [{
        "id": key,
        "type": number(row["type"]),
        "resource_type": number(row["resourceType"]),
        "name": localized(row["name"], names),
        "node_ids": integer_list(row["levellist"]),
        "max_level": number(row["maxLevel"]),
        "group_id": number(row["groupID"]),
    } for key, row in sorted(tables["ResourceSearch"].items())]
    speedups = []
    for item_id, row in tables["Item"].items():
        if atom(row["type"]) != "SpeedUp":
            continue
        speedups.append({
            "item_id": item_id,
            "name": localized(row["name"], names),
            "category": atom(row["typeSub"]),
            "benefit_id": number(row["benefitId"]),
            "quality": number(row["quality"]),
            "duration_minutes": number(row["value"]),
        })
    output_kinds = {
        1016: (1, "Food", "benefit_economy_95"), 1017: (2, "Metal", "benefit_economy_95"),
        1019: (3, "Oil", "benefit_economy_95"), 1027: (5, "Hero EXP", "benefit_economy_33"),
        5042: (99, "Refined Stone", "benefit_economy_93"), 5043: (99, "Steel", "benefit_economy_94"),
    }
    level_rows = defaultdict(list)
    for row in tables["BuildingLevel"].values():
        level_rows[number(row["buildingId"])].append(row)
    producers = []
    for building_id, (kind, output_name, label_key) in output_kinds.items():
        source = tables["Building"][building_id]
        if f'translate="{label_key}"' not in source["info"] or 'funtionKey="speed"' not in source["info"]:
            raise ValueError(f"building {building_id} is not labeled as an output producer")
        producers.append({
            "building_id": building_id,
            "building_name": building_names[building_id],
            "output_type": kind,
            "output_name": output_name,
            "source_ui_label": names[label_key],
            "source_value_field": "BuildingLevel.ability",
            "levels": [
                {"level": number(row["level"]), "base_output_per_hour": number(row["ability"])}
                for row in sorted(level_rows[building_id], key=lambda item: number(item["level"]))
                if number(row["level"]) > 0
            ],
        })
    return {
        "resource_types": {str(key): value for key, value in RESOURCE_TYPES.items()},
        "producer_buildings": producers,
        "world_resource_nodes": nodes,
        "world_search_categories": searches,
        "speedups": sorted(speedups, key=lambda item: (item["category"], item["duration_minutes"])),
    }


def build_heroes(tables, names, benefit_names, building_names):
    heroes = []
    skill_groups = set()
    for hero_id, row in sorted(tables["HeroInfo"].items()):
        if number(row["heroType"]) != 1 or number(row["showType"]) != 1:
            continue
        groups = integer_list(row["skillGroupIds"])
        skill_groups.update(groups)
        heroes.append({
            "id": hero_id,
            "name": localized(row["name"], names),
            "quality": number(row["quality"]),
            "max_level": number(row["maxLevel"]),
            "army_type": number(row["armyType"]),
            "camp_type": number(row["campType"]),
            "fragment_item_id": atom(row["fragmentItemId"]),
            "fragment_count": number(row["fragmentItemCount"]),
            "skill_group_ids": groups,
            "level_curve_id": number(row["template_id"]),
            "training_center": {"building_id": number(row["buildingId"]), "building_name": building_names.get(number(row["buildingId"])), "level": number(row["buildingLevel"])},
            "base_stats": {"hp": number(row["base_php"]), "attack": number(row["base_patk"]), "defense": number(row["base_pdef"])},
            "level_benefits": parse_benefits(row["levelBenefit"], benefit_names),
        })
    level_curves = defaultdict(list)
    for row in tables["HeroLevel"].values():
        level_curves[number(row["template_type"])].append({
            "level": number(row["level"]),
            "costs": parse_resources(row["cost"], names),
            "benefits": parse_benefits(row["levelBenefit"], benefit_names),
        })
    star_curve = []
    for _, row in sorted(tables["HeroStar"].items()):
        star_curve.append({
            "step": number(row["star"]),
            "whole_star": number(row["wholeStar"]),
            "fragment_count": number(row["consumeCount"]),
            "extra_fragment_count": number(row["consumeCountExtra"]),
            "benefits": parse_benefits(row["levelBenefit"], benefit_names),
            "skill_slots": [
                {"level_limit": int(level), "skill_star": int(star)}
                for level, star in re.findall(r"\{levelLimit=(\d+), skillStar=(\d+)\}", row["skillSlot"])
            ],
        })
    skills = []
    for skill_id, row in sorted(tables["NewHeroSkill"].items()):
        if number(row["groupId"]) not in skill_groups:
            continue
        skills.append({
            "id": skill_id,
            "group_id": number(row["groupId"]),
            "star": number(row["star"]),
            "skill_max_level": number(row["skillmaxlevel"]),
            "required_hero_level": number(row["needHeroLevel"]),
            "required_hero_star": number(row["needHeroStarLevel"]),
            "required_exclusive_gear_level": number(row["needExclusiveGearLevel"]),
            "ability": number(row["ability"]),
            "exclusive_gear_ability": number(row["abilityGear"]),
            "cooldown": number(row["cdTime"]),
            "type": number(row["type"]),
        })
    skill_level_curves = defaultdict(list)
    for row in tables["NewHeroSkillLevel"].values():
        skill_level_curves[number(row["heroQuality"])].append({
            "level": number(row["skillLevel"]),
            "ability": number(row["ability"]),
            "costs": parse_resources(row["cost"], names),
        })
    exclusive = []
    strengthen = defaultdict(list)
    for row in tables["HeroExclusiveGearStrengthen"].values():
        strengthen[number(row["group"])].append({
            "level": number(row["level"]), "type": number(row["type"]),
            "fragment_count": number(row["consumeCount"]),
            "requirements": [number(row[f"needLevel{index}"]) for index in range(1, 4)],
            "personal_benefits": parse_benefits(row["personBenefit"], benefit_names),
            "all_hero_benefits": parse_benefits(row["allBenefit"], benefit_names),
        })
    by_id = {hero["id"]: hero["name"] for hero in heroes}
    for _, row in sorted(tables["HeroExclusive"].items()):
        group = number(row["group"])
        exclusive.append({
            "hero_id": number(row["heroID"]), "hero_name": by_id.get(number(row["heroID"])),
            "gear_id": number(row["heroExclusiveGearID"]),
            "shard_item_id": atom(row["exclusiveGearShardID"]),
            "shard_item_name": names.get(atom(row["exclusiveGearShardID"]), atom(row["exclusiveGearShardID"])),
            "shards_per_level": number(row["exclusiveGearShardAmount"]),
            "group": group, "star_limit": number(row["starLimit"]), "strength_limit": number(row["strengthLimit"]),
            "open_conditions": parse_conditions(row["openCondition"]),
            "strengthen_levels": sorted(strengthen[group], key=lambda item: item["level"]),
        })
    exclusive_level_curve = []
    for level_id, row in sorted(tables["HeroExclusiveGearLevel"].items()):
        exclusive_level_curve.append({
            "id": level_id, "skill_max_levels": integer_list(row["skillMaxLevel"]),
            "fragment_count": number(row["consumeCount"]),
            "benefits": parse_benefits(row["levelBenefit"], benefit_names),
        })
    return {
        "playable_heroes": heroes,
        "level_curves": {str(key): sorted(value, key=lambda item: item["level"]) for key, value in sorted(level_curves.items())},
        "star_curve": star_curve,
        "skills": skills,
        "skill_level_curves": {str(key): sorted(value, key=lambda item: item["level"]) for key, value in sorted(skill_level_curves.items())},
        "exclusive_gear": exclusive,
        "exclusive_gear_level_curve": exclusive_level_curve,
    }


def build_equipment(tables, names, benefit_names):
    strengthen = defaultdict(list)
    for row in tables["EquipmentStrengthen"].values():
        strengthen[number(row["equipBaseId"])].append({
            "level": number(row["equipLv"]), "ability": number(row["ability"]),
            "costs": parse_resources(row["cost"], names),
            "client_reward": parse_resources(row["reward"], names),
            "benefits": parse_benefits(row["equipBenefit"], benefit_names),
            "extra_ability": number(row["extraAbility"]),
            "additional_benefits": parse_benefits(row["equipAdditionalBenefit"], benefit_names),
        })
    promotions = defaultdict(list)
    for row in tables["EquipmentPromotion"].values():
        promotions[number(row["equipBaseId"])].append({
            "level": number(row["equipPromotionLv"]), "stage": number(row["equipPromotionStage"]),
            "ability": number(row["ability"]), "costs": parse_resources(row["cost"], names),
            "client_reward": parse_resources(row["reward"], names),
            "benefits": parse_benefits(row["equipBenefit"], benefit_names),
            "extra_ability": number(row["extraAbility"]),
            "additional_benefits": parse_benefits(row["equipAdditionalBenefit"], benefit_names),
        })
    equipment = []
    for equipment_id, row in sorted(tables["EquipmentBase"].items()):
        equipment.append({
            "id": equipment_id, "name": localized(row["name"], names),
            "item_id": atom(row["itemId"]), "quality": number(row["quality"]), "slot": number(row["slot"]),
            "manufacturable": atom(row["manufacturable"]),
            "required_building_level": number(row["unlockBuildingLevel"]),
            "manufacturing_time_seconds": number(row["costTime"]),
            "manufacturing_costs": parse_resources(row["cost"], names),
            "strengthen_levels": sorted(strengthen[equipment_id], key=lambda item: item["level"]),
            "promotion_levels": sorted(promotions[equipment_id], key=lambda item: (item["level"], item["stage"])),
        })
    return {
        "quality_labels": {"2": "Premium", "3": "Good", "4": "SSR", "5": "Mythic"},
        "slot_labels": {"0": "Weapon", "1": "Helmet", "2": "Scope", "3": "Bulletproof Vest"},
        "equipment": equipment,
    }


def build(source_dir, out_dir):
    tables = {}
    manifest_tables = {}
    for name, (guid, expected_hash) in SOURCES.items():
        path = source_dir / f"{name}.lua"
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(f"unexpected hash for {path.name}: {actual_hash}")
        tables[name] = load_table(path)
        manifest_tables[name] = {"bundle_guid": guid, "plaintext_sha256": actual_hash, "rows": len(tables[name])}
    names = load_localization(source_dir)
    benefit_names = {key: localized(row["name"], names) for key, row in tables["DefineBenefit"].items()}
    building_names = {key: localized(row["name"], names) for key, row in tables["Building"].items()}
    progression = build_progression(tables, names, benefit_names)
    resources = build_resources(tables, names, building_names)
    heroes = build_heroes(tables, names, benefit_names, building_names)
    equipment = build_equipment(tables, names, benefit_names)
    unmapped_conditions = [
        condition
        for building in progression["buildings"]
        for condition in building["show_conditions"] + [condition for level in building["levels"] for condition in level["prerequisites"]]
        if condition["kind"] == "unmapped"
    ]
    incomplete_buildings = [building["id"] for building in progression["buildings"] if not building["level_rows_complete"]]
    unmapped_resource_types = sorted({node["type"] for node in resources["world_resource_nodes"] if node["type"] not in RESOURCE_TYPES})
    unsupported_research_levels = sum(not level["static_optimizer_supported"] for tech in progression["research"] for level in tech["levels"])
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "progression.json", progression)
    write_json(out_dir / "resources.json", resources)
    write_json(out_dir / "heroes.json", heroes)
    write_json(out_dir / "equipment.json", equipment)
    write_json(out_dir / "model-manifest.json", {
        "source": {"package": "com.zroute.global", "app_version": "1.30.07", "catalog_version": "V202608062022", "client_build_time": "2026-08-06 20:26:03"},
        "tables": manifest_tables,
        "localization_plaintext_sha256": LANG_HASHES,
        "scope": "Static client facts for progression analysis; no player, alliance, event, or server state.",
        "coverage": {
            "unmapped_building_condition_instances": len(unmapped_conditions),
            "unmapped_building_condition_ids": sorted({item["id"] for item in unmapped_conditions}),
            "buildings_with_incomplete_level_rows": incomplete_buildings,
            "unmapped_world_resource_type_ids": unmapped_resource_types,
            "research_levels_requiring_external_or_unmapped_state": unsupported_research_levels,
        },
        "optimizer_joins": [
            "building level -> prerequisite conditions + time + costs",
            "research level -> prerequisite conditions + time + costs + benefits",
            "VIP level -> building speed percent",
            "producer building level -> base output per hour",
            "hero -> level curve + star curve + skill groups + training-center gate",
            "equipment base -> manufacturing + strengthening + promotion",
            "speedup item -> category + duration minutes",
        ],
        "caveats": [
            "BuildingProduction and BuildingEffect are empty in this client build; producer output uses BuildingLevel.ability where the UI labels it output per hour.",
            "An action with static_optimizer_supported=false must not be planned without resolving its parent gate, missing row, or unmapped condition externally.",
            "Building max_level is the configured value; available_max_level and level_rows_complete expose whether matching level rows exist.",
            "ResourceInfo.speed units are not confirmed, so resources.json preserves speed_value without deriving gather duration.",
            "World resource types 51, 52, and 53 have no confirmed English label in the extracted localization set.",
            "Refined Stone and Steel producer output_type 99 means an item resource; the product labels come from the building UI and are not item-ID joins.",
            "HeroInfo contains mode/copy rows; heroes.json includes only heroType=1 and showType=1 rows.",
            "No direct construction, research, production, or gathering benefit appears in playable HeroInfo.levelBenefit rows.",
            "Client reward fields are preserved as client_reward and are not treated as upgrade costs.",
            "Dynamic server, event, alliance-help, player-inventory, queue, and active-buff state must be supplied before an optimizer can recommend a live route.",
        ],
    })
    check(out_dir)


def check(out_dir):
    progression = json.loads((out_dir / "progression.json").read_text(encoding="utf-8"))
    resources = json.loads((out_dir / "resources.json").read_text(encoding="utf-8"))
    heroes = json.loads((out_dir / "heroes.json").read_text(encoding="utf-8"))
    equipment = json.loads((out_dir / "equipment.json").read_text(encoding="utf-8"))
    manifest = json.loads((out_dir / "model-manifest.json").read_text(encoding="utf-8"))
    assert len(progression["buildings"]) == 99 and len(progression["research"]) == 328 and len(progression["benefits"]) == 359
    assert progression["construction_modifiers"]["vip_building_speed_percent_by_level"] == [0, 0, 0, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 50, 50, 50, 50, 50, 50]
    assert len(resources["world_resource_nodes"]) == 190 and len(resources["world_search_categories"]) == 20
    assert len(resources["producer_buildings"]) == 6 and len(resources["speedups"]) == 40
    assert len(heroes["playable_heroes"]) == 32 and len(heroes["star_curve"]) == 26 and len(heroes["exclusive_gear"]) == 3
    assert len(equipment["equipment"]) == 16
    assert sum(len(item["strengthen_levels"]) for item in equipment["equipment"]) == 356
    assert sum(len(item["promotion_levels"]) for item in equipment["equipment"]) == 104
    assert {item["level_curve_id"] for item in heroes["playable_heroes"]} == {1, 2}
    assert {item["group_id"] for item in heroes["skills"]} == {group for hero in heroes["playable_heroes"] for group in hero["skill_group_ids"]}
    base = next(item for item in progression["buildings"] if item["id"] == 1001)
    assert base["name"] == "Base" and len(base["levels"]) == 30 and base["levels"][-1]["level"] == 30
    assert manifest["tables"]["EquipmentBase"]["rows"] == 16
    assert manifest["coverage"]["buildings_with_incomplete_level_rows"] == [20002, 20014]
    assert manifest["coverage"]["unmapped_world_resource_type_ids"] == [51, 52, 53]
    assert all(
        not level["static_optimizer_supported"]
        for building in progression["buildings"] for level in building["levels"]
        if level["requires_external_state"]
    )
    assert all(
        not level["static_optimizer_supported"]
        for tech in progression["research"] for level in tech["levels"]
        if level["requires_external_state"]
    )
    check_base(out_dir)
    print("ok: 99 buildings, 328 research techs, 32 heroes, 16 equipment bases, 190 resource nodes")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("build")
    generate.add_argument("source_dir", type=Path)
    generate.add_argument("out_dir", type=Path)
    verify = commands.add_parser("check")
    verify.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    build(args.source_dir, args.out_dir) if args.command == "build" else check(args.out_dir)


if __name__ == "__main__":
    main()
