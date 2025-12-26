#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# COMMAND FOR START 
#   python .\make_datapack.py --csv ".\summary.csv" --out ".\lwi_loot_datapack"
import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


PACK_FORMAT_1_20_1 = 15  # Minecraft 1.20.1

VILLAGE_CHEST_DESTS = [
    (241, 65, 471),
    (225, 65, 497),
    (247, 65, 455),
    (218, 65, 450),
    (187, 65, 452),
    (174, 65, 472),
    (193, 65, 482),
    (162, 65, 485),
]

def build_update_chests_function(
    base_x: int, y: int, z: int, houses: int, step_x: int,
    dests: List[Tuple[int, int, int]],
    dimension: str = "minecraft:overworld",
) -> str:
    """
    Copies (clones) already-generated chests from the staging row:
      (base_x + i*step_x, y, z)
    into the village house coordinates in dests.

    NOTE: /clone needs the source area loaded, and destination chunks loaded too.
    """
    lines = [
        "# Copy pre-generated chests from staging row into village houses",
        "# Run: /function village:update_chests",
        "",
    ]

    n = min(houses, len(dests))
    if n <= 0:
        return "\n".join(lines) + "\n"

    for i in range(n):
        sx = base_x + i * step_x
        sy = y
        sz = z
        dx, dy, dz = dests[i]

        # clone single block (chest) with NBT
        lines.append(
            f"execute in {dimension} run clone {sx} {sy} {sz} {sx} {sy} {sz} {dx} {dy} {dz} replace"
        )

    lines.append("")
    return "\n".join(lines)


def read_summary_csv(csv_path: Path) -> Tuple[List[Dict], Dict[str, int], List[str]]:
    """
    Returns:
      guns_rows: list of dict rows for index/guns
      ammo_stack: ammo_id -> stack_size (int)
      attachments_ids: list of attachment ids (index_id)
    """
    guns_rows: List[Dict] = []
    ammo_stack: Dict[str, int] = {}
    attachments_ids: List[str] = []

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            src = (r.get("source") or "").strip()
            cat = (r.get("category") or "").strip()
            idx_id = (r.get("index_id") or "").strip()
            if not idx_id:
                continue

            if src == "index" and cat == "guns":
                guns_rows.append(r)

            if src == "index" and cat == "ammo":
                # stack_size может быть пустым/float-строкой
                ss = (r.get("stack_size") or "").strip()
                try:
                    stack = int(float(ss)) if ss else 60
                except Exception:
                    stack = 60
                ammo_stack[idx_id] = stack

            if src == "index" and cat == "attachments":
                attachments_ids.append(idx_id)

    # uniq
    attachments_ids = sorted(set(attachments_ids))
    return guns_rows, ammo_stack, attachments_ids


def filter_simple_guns(guns_rows: List[Dict]) -> Tuple[List[str], List[str], List[str]]:
    """
    Берём "простые" классы: pistol/shotgun/rifle
    Возвращаем списки index_id.
    """
    pistols, shotguns, rifles = [], [], []
    for r in guns_rows:
        gun_id = (r.get("index_id") or "").strip()
        gtype = (r.get("type") or "").strip().lower()

        if not gun_id or not gtype:
            continue

        if gtype == "pistol":
            pistols.append(gun_id)
        elif gtype == "shotgun":
            shotguns.append(gun_id)
        elif gtype == "rifle":
            rifles.append(gun_id)

    # uniq
    pistols = sorted(set(pistols))
    shotguns = sorted(set(shotguns))
    rifles = sorted(set(rifles))
    return pistols, shotguns, rifles


def gun_entry(gun_id: str, weight: int = 1) -> Dict:
    # TaCZ gun item uses GunId in tag
    return {
        "type": "minecraft:item",
        "name": "tacz:modern_kinetic_gun",
        "weight": weight,
        "functions": [
            {"function": "minecraft:set_nbt", "tag": f'{{GunId:"{gun_id}"}}'}
        ],
    }


def ammo_entry(ammo_id: str, max_stack: int, weight: int = 1) -> Dict:
    # random count: min 10, max = min(stack, 60) (на всякий)
    mx = max(1, min(max_stack, 60))
    mn = min(10, mx)
    return {
        "type": "minecraft:item",
        "name": "tacz:ammo",
        "weight": weight,
        "functions": [
            {"function": "minecraft:set_nbt", "tag": f'{{AmmoId:"{ammo_id}"}}'},
            {"function": "minecraft:set_count", "count": {"min": mn, "max": mx}},
        ],
    }


def attachment_entry(att_id: str, weight: int = 1) -> Dict:
    return {
        "type": "minecraft:item",
        "name": "tacz:attachment",
        "weight": weight,
        "functions": [
            {"function": "minecraft:set_nbt", "tag": f'{{AttachmentId:"{att_id}"}}'}
        ],
    }


def write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def build_house_loot_table(
    pistols: List[str],
    shotguns: List[str],
    rifles: List[str],
    ammo_stack: Dict[str, int],
    attachments: List[str],
    ak_id: Optional[str] = None,
) -> Dict:
    """
    Loot table for one house:
    - supplies pool
    - resources pool
    - gun pool (simple guns)
    - ammo pool
    - attachments pool
    - optional guaranteed AK pool
    """
    # базовый лут
    supplies_entries = [
        {"type": "minecraft:item", "name": "minecraft:bread",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 4, "max": 16}}]},
        {"type": "minecraft:item", "name": "minecraft:cooked_beef",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 2, "max": 10}}]},
        {"type": "minecraft:item", "name": "minecraft:torch",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 8, "max": 48}}]},
        {"type": "minecraft:item", "name": "minecraft:oak_planks",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 16, "max": 64}}]},
        {"type": "minecraft:item", "name": "minecraft:oak_log",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 8, "max": 32}}]},
    ]

    resources_entries = [
        {"type": "minecraft:item", "name": "minecraft:iron_ingot",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 2, "max": 16}}]},
        {"type": "minecraft:item", "name": "minecraft:coal",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 4, "max": 24}}]},
        {"type": "minecraft:item", "name": "minecraft:string",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 2, "max": 12}}]},
        {"type": "minecraft:item", "name": "minecraft:leather",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 1, "max": 8}}]},
        {"type": "minecraft:item", "name": "minecraft:golden_apple",
         "functions": [{"function": "minecraft:set_count", "count": {"min": 0, "max": 2}}]},
    ]

    # guns: делаем баланс — пистолет чаще, дробовик/винтовка реже
    gun_entries: List[Dict] = []
    for g in pistols:
        gun_entries.append(gun_entry(g, weight=6))
    for g in shotguns:
        gun_entries.append(gun_entry(g, weight=3))
    for g in rifles:
        gun_entries.append(gun_entry(g, weight=2))

    # ammo: берем все ammo из index, веса равные
    ammo_entries: List[Dict] = []
    for ammo_id, stack in ammo_stack.items():
        ammo_entries.append(ammo_entry(ammo_id, stack, weight=1))

    # attachments: берём все обвесы, но с 0–1 выпадением в доме
    att_entries = [attachment_entry(a, weight=1) for a in attachments]

    pools = [
        {
            "rolls": {"min": 2, "max": 5},
            "entries": supplies_entries
        },
        {
            "rolls": {"min": 0, "max": 3},
            "entries": resources_entries
        },
        {
            "rolls": {"min": 0, "max": 1},
            "entries": gun_entries
        },
        {
            "rolls": {"min": 0, "max": 2},
            "entries": ammo_entries
        },
        {
            "rolls": {"min": 0, "max": 1},
            "entries": att_entries
        },
    ]

    # Гарантированный AK (в одном доме отдельной таблицей)
    if ak_id:
        pools.insert(2, {  # ближе к началу
            "rolls": 1,
            "entries": [gun_entry(ak_id, weight=1)]
        })

    return {"type": "minecraft:chest", "pools": pools}


def build_fill_function(
    base_x: int, y: int, z: int, houses: int, step_x: int,
    normal_table: str, ak_table: str, ak_house_index: int
) -> str:
    """
    Creates mcfunction text. One house uses ak_table.
    ak_house_index: 0-based index (0..houses-1)
    """
    lines = []
    for i in range(houses):
        x = base_x + i * step_x
        lines.append(f"setblock {x} {y} {z} minecraft:chest")
        table = ak_table if i == ak_house_index else normal_table
        lines.append(f'data merge block {x} {y} {z} {{LootTable:"{table}"}}')
        lines.append("")  # spacer
    return "\n".join(lines).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate Minecraft datapack from TaCZ summary.csv for loot chests.")
    ap.add_argument("--csv", required=True, help="Path to summary.csv (from your scan)")
    ap.add_argument("--out", required=True, help="Output datapack folder (will be created)")
    ap.add_argument("--namespace", default="village", help="Datapack namespace (default: village)")

    # village placement
    ap.add_argument("--base-x", type=int, default=282)
    ap.add_argument("--y", type=int, default=55)
    ap.add_argument("--z", type=int, default=491)
    ap.add_argument("--houses", type=int, default=8)
    ap.add_argument("--step-x", type=int, default=2)

    # AK placement
    ap.add_argument("--ak-id", default="tacz:ak47", help="Gun id to guarantee once (default: tacz:ak47)")
    ap.add_argument("--ak-house-index", type=int, default=3, help="0-based house index to contain guaranteed AK (default: 3)")

    args = ap.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    out_root = Path(args.out).expanduser().resolve()
    ns = args.namespace.strip()

    guns_rows, ammo_stack, attachments = read_summary_csv(csv_path)
    pistols, shotguns, rifles = filter_simple_guns(guns_rows)

    if not pistols and not shotguns and not rifles:
        raise SystemExit("No simple guns found (pistol/shotgun/rifle) in summary.csv")

    # Проверим, что ak_id реально есть в gun list, иначе просто не гарантируем
    all_simple = set(pistols + shotguns + rifles)
    ak_id = args.ak_id.strip()
    if ak_id not in all_simple:
        # всё равно попробуем — вдруг ak_id есть, но не входит в simple фильтр
        # (например, type у него другой). Но для безопасности:
        ak_id = args.ak_id.strip()

    # datapack structure
    pack_dir = out_root
    data_dir = pack_dir / "data" / ns
    functions_dir = data_dir / "functions"
    loot_dir = data_dir / "loot_tables" / "chests"

    pack_dir.mkdir(parents=True, exist_ok=True)

    # pack.mcmeta
    write_json(pack_dir / "pack.mcmeta", {
        "pack": {
            "pack_format": PACK_FORMAT_1_20_1,
            "description": "LWI loot generator (auto)"
        }
    })

    # loot tables
    normal_table_name = f"{ns}:chests/house"
    ak_table_name = f"{ns}:chests/house_ak"

    house_table = build_house_loot_table(
        pistols=pistols,
        shotguns=shotguns,
        rifles=rifles,
        ammo_stack=ammo_stack,
        attachments=attachments,
        ak_id=None
    )
    house_ak_table = build_house_loot_table(
        pistols=pistols,
        shotguns=shotguns,
        rifles=rifles,
        ammo_stack=ammo_stack,
        attachments=attachments,
        ak_id=ak_id
    )

    write_json(loot_dir / "house.json", house_table)
    write_json(loot_dir / "house_ak.json", house_ak_table)

    # function
    fn_text = build_fill_function(
        base_x=args.base_x, y=args.y, z=args.z,
        houses=args.houses, step_x=args.step_x,
        normal_table=normal_table_name,
        ak_table=ak_table_name,
        ak_house_index=args.ak_house_index
    )
    functions_dir.mkdir(parents=True, exist_ok=True)
    (functions_dir / "fill_village.mcfunction").write_text(fn_text, encoding="utf-8")

        # function: update_chests (clone generated chests into real village coords)
    update_text = build_update_chests_function(
        base_x=args.base_x, y=args.y, z=args.z,
        houses=args.houses, step_x=args.step_x,
        dests=VILLAGE_CHEST_DESTS,
        dimension="minecraft:overworld",
    )
    (functions_dir / "update_chests.mcfunction").write_text(update_text, encoding="utf-8")
    print("Functions to run in-game:")
    print(" - /function " + ns + ":fill_village")
    print(" - /function " + ns + ":update_chests")


    print("Datapack generated:", pack_dir)
    print("Function to run in-game: /function " + ns + ":fill_village")
    print("Loot tables:")
    print(" -", loot_dir / "house.json")
    print(" -", loot_dir / "house_ak.json")


if __name__ == "__main__":
    main()
