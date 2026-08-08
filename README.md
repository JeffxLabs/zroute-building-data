# Z Route: Redemption progression data

This repository turns static progression facts from Android client version `1.30.07` into machine-readable JSON for route planning and leveling analysis. It covers buildings, research, resource generation and gathering nodes, speedups, playable heroes, hero progression, and equipment. The original Base level 1–30 CSV remains available for spreadsheet use.

Use the interactive [Z Route Base Planner](https://jfryton.github.io/zroute-building-data/) to select only your current Base level or enter every relevant building level and calculate the remaining route.

## Data

- [`data/base-upgrades.csv`](data/base-upgrades.csv) is the compact, spreadsheet-friendly dataset.
- [`data/base-upgrades.json`](data/base-upgrades.json) preserves the prerequisite structure and source metadata.
- [`data/progression.json`](data/progression.json) joins 99 buildings and 328 research technologies to their levels, prerequisites, base times, costs, and benefits. It also defines 359 benefit types and the VIP 0–18 Building Speed curve.
- [`data/resources.json`](data/resources.json) contains six production-building curves, 190 world resource nodes, 20 search categories, and 40 speedup items.
- [`data/heroes.json`](data/heroes.json) contains 32 playable heroes, two level curves, the global star curve, their skill progressions, training-center gates, and three exclusive-gear paths.
- [`data/equipment.json`](data/equipment.json) joins all 16 equipment bases to manufacturing, strengthening, and Mythic promotion data.
- [`data/model-manifest.json`](data/model-manifest.json) pins source hashes and records model joins and uncertainty boundaries.
- [`docs/base-leveling-guide.svg`](docs/base-leveling-guide.svg) is a visual Base level 1–30 guide with Base time, combined Base/prerequisite resources, and per-building prerequisite time for parallel scheduling.

All JSON values are direct client-table facts or explicitly identified interpretations. Raw tables, localization assets, bundles, and APKs are not included.

## Optimizer model

The static files support a dependency graph whose actions are building upgrades, research levels, hero levels/stars/skills, and equipment manufacturing/upgrades. Each action supplies its gate, client base time, and resource cost; research and gear actions also expose their client benefit values. A solver can derive marginal benefit by comparing adjacent levels. Producer building `ability` values are published as `base_output_per_hour` because the matching client UI labels them “Output per Hour.”

A live recommendation still needs an account-state input: current building/research/hero/gear levels, Food/Metal/Oil and item inventories, active queues, speedups, current percentage modifiers, alliance help, event/server modifiers, and the target objective. Those dynamic values are intentionally not guessed. `ResourceInfo.speed` is retained as `speed_value` because its unit and gathering-duration formula are not yet confirmed.

Conditions preserve their numeric parameters and include a semantic `kind` where confirmed. Conditions in a prerequisite list are jointly required; `any_building_in_list_level` is the client’s internal OR case. A planner can resolve `building_level`, `research_level`, and `any_building_class_level` against IDs/classes in `progression.json`; seasonal and event gates need live server state. Building levels expose `static_optimizer_supported` and `requires_external_state`; a solver should reject unsupported levels rather than treating an unknown gate as satisfied. Two event/decor buildings also expose `level_rows_complete=false` because their configured maximum exceeds the available client rows.

Hero rows are limited to client records where `heroType=1` and `showType=1`, excluding mode/copy records. Their `level_curve_id` joins to `level_curves`, and `skill_group_ids` join to `skills`. No direct construction, research, production, or gathering modifier appears in the playable heroes’ `levelBenefit` records in this version.

All prerequisite entries on a level must pass. Condition `20103` requires the named building to reach the minimum level; condition `20105` requires any one building in its group to reach the minimum. The group used here is Warrior, Tactical, or Assault Training Center.

Times are seconds from the client table before construction-speed bonuses, alliance help, events, or server-side overrides. The planner can apply the client VIP curve, Quick Construction I–IV research, an additional speed percentage, and a user-supplied free-finish threshold. The client identifies survivor benefit `20006` as “Free Building Speedup Time +”; it extends the point at which a build can be finished free rather than adding Building Speed. Costs use the English client names for resource types 1–3: Food, Metal, and Oil. The Base rows have no `specialCost`; the separate table `reward` field is intentionally not reported as a cost.

The generated sheet caption still mentions “L35,” but the live Base definition has `maxLv = 30` and the client contains no Base upgrade rows above level 30.

## Reproduce

Both generators use only Python's standard library. The complete model expects the pinned plaintext tables and five English localization JSON files listed in `model-manifest.json`; no source assets belong in this repository.

```sh
python3 tools/extract_base.py build /path/to/decrypted-tables /path/to/lang_building data
python3 tools/extract_model.py build /path/to/decrypted-tables data
python3 tools/extract_model.py check data
python3 tools/render_base_guide.py data/base-upgrades.json data/progression.json docs/base-leveling-guide.svg
```

Querying the model needs no custom library:

```sh
python3 - <<'PY'
import json
model = json.load(open("data/progression.json"))
base = next(item for item in model["buildings"] if item["id"] == 1001)
print(base["levels"][29])
PY
```

The complete-model generator verifies every source hash so a different client version cannot silently produce mislabeled data. The smaller Base-only generator remains available for its focused CSV workflow.

For the Base dataset specifically:

```sh
python3 tools/extract_base.py check data
```

The source directory must contain `Building.lua`, `BuildingLevel.lua`, and `BuildingUpgrade.lua`. Their expected hashes are pinned in the generator so a different client version cannot silently produce mislabeled data.

## Source provenance

| Item | Value |
| --- | --- |
| Android package | `com.zroute.global` |
| App version | `1.30.07` |
| Catalog package/version | `P1` / `V202608062022` |
| Catalog client build time | `2026-08-06 20:26:03` |
| APK archive SHA-256 | `390cc17ce0c2fb9230055ee6aaa5c8a49cdae64c14926660da2dedb242937ec0` |
| `base.apk` SHA-256 | `76a80fed49fee35b932e4766a32b13a08e947731fccbe91400b013b725608720` |
| `base_assets.apk` SHA-256 | `e7a1b56d15d80880615b1944c9329b56313c1b92121ee08d3438c5242c598a13` |
| `config.arm64_v8a.apk` SHA-256 | `0de42b6b90dcb700c3b4fa09d5c70fe72931f8f9ece6db2de9b6f165e2c4facb` |
| Unity app GUID | `fc8846b3-f8ce-4c94-8eef-9523dcb8feb8` |

The relevant bundles are bytewise XOR-obfuscated with `0x10`. After UnityFS extraction, their TextAsset payloads use AES-256-ECB with PKCS#7 padding and client key `3@!1$592-5#58N7W3z3&C6%D43&83~79`.

| Table | Bundle GUID | Plaintext SHA-256 |
| --- | --- | --- |
| `Building.lua` | `0eb19f215674df0a721e8af4b6e38b27` | `626e8c94253acbc3d62e35a48995c1672224ae41ef77b16d2ef82a94e73ae9a8` |
| `BuildingLevel.lua` | `fe3de944af769d3aed3c085028a01388` | `c011f412e2d8b3de100df0c4dd7605718950b30729adee240a9746a2f42208d9` |
| `BuildingUpgrade.lua` | `867eafd983c72fabb00169f6995b94ed` | `ec2855a231be5bc764f831c13abf44fc4814f6c04f53a040e2448856b95668ba` |
| `VipPrivilege.lua` | `557146594caa9ac60a1eb7fa8b53ee1f` | `99bfc9ed88d0f3ffaa14807c8302f4b947d4a3b64ed4b6444ae3ec920971383c` |
| `lang_building` | `5c86b0882980ee813ddddd26a83b5bcb` | `a2d6dc3657aaf825a5a163b0fac769bad78d212e1ffcd41ebda3d64291f0bc82` |

Only derived facts and the generator are checked in—no APK, bundle, native library, raw localization file, or decrypted client table is included.
