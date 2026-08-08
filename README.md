# Z Route: Redemption Base upgrade data

This repository documents the Base (building ID `1001`) upgrade requirements embedded in the Android client version `1.30.07`. The client contains complete Base rows for target levels 1–30: base time, Food/Metal/Oil costs, and building prerequisites.

## Data

- [`data/base-upgrades.csv`](data/base-upgrades.csv) is the compact, spreadsheet-friendly dataset.
- [`data/base-upgrades.json`](data/base-upgrades.json) preserves the prerequisite structure and source metadata.

All prerequisite entries on a level must pass. Condition `20103` requires the named building to reach the minimum level; condition `20105` requires any one building in its group to reach the minimum. The group used here is Warrior, Tactical, or Assault Training Center.

Times are seconds from the client table before construction-speed bonuses, alliance help, events, or server-side overrides. Costs use the English client names for resource types 1–3: Food, Metal, and Oil. The Base rows have no `specialCost`; the separate table `reward` field is intentionally not reported as a cost.

The generated sheet caption still mentions “L35,” but the live Base definition has `maxLv = 30` and the client contains no Base upgrade rows above level 30.

## Reproduce

The generator uses only Python's standard library. Give it the three locally decrypted client tables and the locally extracted `lang_building` JSON; no source assets belong in this repository.

```sh
python3 tools/extract_base.py build /path/to/decrypted-tables /path/to/lang_building data
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
| `lang_building` | `5c86b0882980ee813ddddd26a83b5bcb` | `a2d6dc3657aaf825a5a163b0fac769bad78d212e1ffcd41ebda3d64291f0bc82` |

Only derived facts and the generator are checked in—no APK, bundle, native library, raw localization file, or decrypted client table is included.
