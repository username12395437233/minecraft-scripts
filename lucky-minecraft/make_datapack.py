#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# COMMAND FOR START:
#   python .\make_datapack.py --csv ".\summary.csv" --out ".\lwi_loot_datapack"

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================
# CONFIG (EDIT HERE)
# ============================================================

# Minecraft datapack format
PACK_FORMAT = 15  # Minecraft 1.20.1

# Namespace inside datapack (folder data/<NAMESPACE>/...)
DEFAULT_NAMESPACE = "village"

# --- STAGING ROW (where chests are generated/filled first)
STAGING_DIMENSION = "minecraft:overworld"
STAGING_BASE_X = 282
STAGING_Y = 55
STAGING_Z = 491
STAGING_HOUSES = 8
STAGING_STEP_X = 2

SPAWN_AROUND_CHESTS = True
SPAWN_RADIUS_MIN = 5
SPAWN_RADIUS_MAX = 20

# сколько и каких мобов на каждый сундук
MOBS_PER_CHEST = [
    ("minecraft:zombie", 2, '{PersistenceRequired:1b}'),
    ("minecraft:skeleton", 1, '{PersistenceRequired:1b}'),
    ("minecraft:spider", 1, '{PersistenceRequired:1b}'),
]

# --- DESTINATIONS (where chests should be cloned into village houses)
# IMPORTANT: /clone requires loaded chunks for BOTH source and destination!
VILLAGE_CHEST_DESTS: List[Tuple[int, int, int]] = [
    (241, 65, 471),
    (225, 65, 497),
    (247, 65, 455),
    (218, 65, 450),
    (187, 65, 452),
    (174, 65, 472),
    (193, 65, 482),
    (162, 65, 485),
]

# Optional: allow overriding destinations via CSV (--dest-csv)
ENABLE_DEST_CSV_OVERRIDE = True

# --- LOOT SETTINGS
# Gun weights (relative chance inside gun pool)
WEIGHT_PISTOL = 10
WEIGHT_SHOTGUN = 10
WEIGHT_RIFLE = 1

# Rolls per pool (min/max)
ROLLS_SUPPLIES = (2, 5)
ROLLS_RESOURCES = (0, 3)
ROLLS_GUNS = (1, 2)
ROLLS_AMMO_GENERAL = (1, 3)
ROLLS_ATTACHMENTS = (0, 1)

# Shotgun ammo boost:
# If True and shotgun ammo exists, add a special pool for shotgun ammo.
ENABLE_SHOTGUN_AMMO_POOL = True
ROLLS_AMMO_SHOTGUN = (1, 2)
WEIGHT_AMMO_SHOTGUN = 15
WEIGHT_AMMO_GENERAL = 3

# Ammo count per drop: min/max derived from stack_size, capped at MAX_AMMO_STACK_CAP
AMMO_MIN_PER_DROP = 16
MAX_AMMO_STACK_CAP = 64  # never set count above this even if stack_size is larger

# If ammo_id for a shotgun isn't found in index/ammo, use this stack fallback
AMMO_STACK_FALLBACK_IF_MISSING = 36

# Attachments weight
WEIGHT_ATTACHMENT = 1

# Guaranteed AK in one house loot table
DEFAULT_AK_ID = "tacz:ak47"
DEFAULT_AK_HOUSE_INDEX = 3  # 0-based

# Default fire modes if not found in CSV
DEFAULT_FIREMODE_PISTOL = "SEMI"
DEFAULT_FIREMODE_SHOTGUN = "SEMI"
DEFAULT_FIREMODE_RIFLE = "AUTO"

# --- VANILLA LOOT CONTENT (edit items/amounts)
SUPPLIES_ENTRIES = [
    {"name": "minecraft:bread", "min": 4, "max": 16},
    {"name": "minecraft:cooked_beef", "min": 2, "max": 10},
    {"name": "minecraft:torch", "min": 8, "max": 48},
    {"name": "minecraft:oak_planks", "min": 16, "max": 64},
    {"name": "minecraft:oak_log", "min": 8, "max": 32},
]

RESOURCES_ENTRIES = [
    {"name": "minecraft:iron_ingot", "min": 2, "max": 16},
    {"name": "minecraft:coal", "min": 4, "max": 24},
    {"name": "minecraft:string", "min": 2, "max": 12},
    {"name": "minecraft:leather", "min": 1, "max": 8},
    {"name": "minecraft:golden_apple", "min": 0, "max": 2},
]

# ============================================================
# END CONFIG
# ============================================================

def build_spawn_mobs_function(
    chest_coords: List[Tuple[int, int, int]],
    mobs_per_chest: List[Tuple[str, int, str]],
    rmin: int,
    rmax: int,
    dimension: str = "minecraft:overworld",
) -> str:
    lines: List[str] = []
    lines.append("# One-time spawn mobs around chests")
    lines.append("# Run: /function village:spawn_mobs")
    lines.append("# WARNING: chunks must be loaded (destinations)!")
    lines.append("")

    for i, (x, y, z) in enumerate(chest_coords, start=1):
        tag = f"village_c{i}"
        lines.append(f"# ---- Chest {i}: {x} {y} {z} ----")

        # summon markers at chest center, tagged by mob type
        for mob_id, count, _nbt in mobs_per_chest:
            mob_tag = "mob_" + mob_id.split(":", 1)[1]
            for _ in range(int(count)):
                lines.append(
                    f'execute in {dimension} run summon minecraft:marker {x} {y} {z} '
                    f'{{Tags:["village_tmp","{tag}","{mob_tag}"]}}'
                )

        # spread markers
        lines.append(
            f"execute in {dimension} run spreadplayers {x} {z} {rmin} {rmax} false "
            f"@e[type=minecraft:marker,tag=village_tmp,tag={tag},distance=..1]"
        )

        # summon mobs at markers (simple air + solid-under check)
        for mob_id, _count, nbt in mobs_per_chest:
            mob_tag = "mob_" + mob_id.split(":", 1)[1]
            lines.append(
                f"execute in {dimension} as @e[type=minecraft:marker,tag=village_tmp,tag={tag},tag={mob_tag}] "
                f"at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air "
                f"run summon {mob_id} ~ ~ ~ {nbt}"
            )

        # cleanup markers within radius (rmax + запас)
        lines.append(
            f"execute in {dimension} run kill "
            f"@e[type=minecraft:marker,tag=village_tmp,tag={tag},distance=..{rmax + 5}]"
        )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def load_destinations_csv(path: Path) -> List[Tuple[int, int, int]]:
    """
    CSV format (with header):
      x,y,z
    or without header:
      241,65,471
    """
    dests: List[Tuple[int, int, int]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        sample = f.read(2048)
        f.seek(0)

        has_header = any(h in sample.lower() for h in ["x", "y", "z"])
        if has_header:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    x = int(float((r.get("x") or "").strip()))
                    y = int(float((r.get("y") or "").strip()))
                    z = int(float((r.get("z") or "").strip()))
                    dests.append((x, y, z))
                except Exception:
                    continue
        else:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                try:
                    x = int(float(str(row[0]).strip()))
                    y = int(float(str(row[1]).strip()))
                    z = int(float(str(row[2]).strip()))
                    dests.append((x, y, z))
                except Exception:
                    continue

    # uniq & stable
    seen = set()
    out: List[Tuple[int, int, int]] = []
    for t in dests:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def build_update_chests_function(
    base_x: int, y: int, z: int, houses: int, step_x: int,
    dests: List[Tuple[int, int, int]],
    dimension: str = "minecraft:overworld",
) -> str:
    lines = [
        "# Copy pre-generated chests from staging row into village houses",
        "# Run: /function village:update_chests",
        "# WARNING: /clone needs chunks loaded for source and destination!",
        "",
    ]

    n = min(houses, len(dests))
    if n <= 0:
        lines.append("# No destinations/houses to process.")
        return "\n".join(lines) + "\n"

    for i in range(n):
        sx = base_x + i * step_x
        dx, dy, dz = dests[i]
        lines.append(
            f"execute in {dimension} run clone {sx} {y} {z} {sx} {y} {z} {dx} {dy} {dz} replace"
        )

    lines.append("")
    return "\n".join(lines)


def read_summary_csv(csv_path: Path) -> Tuple[List[Dict], Dict[str, int], List[str], Dict[str, str], Dict[str, str]]:
    """
    Returns:
      guns_rows: list of dict rows for index/guns
      ammo_stack: ammo_id -> stack_size (int)
      attachments_ids: list of attachment ids (index_id)
      gun_to_ammo: gun_id -> ammo_id
      gun_to_firemode: gun_id -> "AUTO"/"SEMI"/"BURST"/""
    """
    guns_rows: List[Dict] = []
    ammo_stack: Dict[str, int] = {}
    attachments_ids: List[str] = []
    gun_to_ammo: Dict[str, str] = {}
    gun_to_firemode: Dict[str, str] = {}

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

                ga = (r.get("gun_ammo") or "").strip()
                if ga:
                    gun_to_ammo[idx_id] = ga

                fm = (r.get("default_fire_mode") or "").strip()
                if fm:
                    gun_to_firemode[idx_id] = fm

            if src == "index" and cat == "ammo":
                ss = (r.get("stack_size") or "").strip()
                try:
                    stack = int(float(ss)) if ss else 60
                except Exception:
                    stack = 60
                ammo_stack[idx_id] = stack

            if src == "index" and cat == "attachments":
                attachments_ids.append(idx_id)

    attachments_ids = sorted(set(attachments_ids))
    return guns_rows, ammo_stack, attachments_ids, gun_to_ammo, gun_to_firemode


def filter_simple_guns(guns_rows: List[Dict]) -> Tuple[List[str], List[str], List[str]]:
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

    return sorted(set(pistols)), sorted(set(shotguns)), sorted(set(rifles))


def gun_entry(gun_id: str, fire_mode: str = "", weight: int = 1) -> Dict:
    tag_parts = [f'GunId:"{gun_id}"']
    if fire_mode:
        tag_parts.append(f'GunFireMode:"{fire_mode}"')
    tag = "{" + ",".join(tag_parts) + "}"

    return {
        "type": "minecraft:item",
        "name": "tacz:modern_kinetic_gun",
        "weight": weight,
        "functions": [{"function": "minecraft:set_nbt", "tag": tag}],
    }


def ammo_entry(ammo_id: str, max_stack: int, weight: int = 1) -> Dict:
    try:
        ms = int(max_stack) if max_stack else MAX_AMMO_STACK_CAP
    except Exception:
        ms = MAX_AMMO_STACK_CAP

    mx = max(1, min(ms, MAX_AMMO_STACK_CAP))
    mn = min(AMMO_MIN_PER_DROP, mx)

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
        "functions": [{"function": "minecraft:set_nbt", "tag": f'{{AttachmentId:"{att_id}"}}'}],
    }


def write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _vanilla_item_entry(item_name: str, mn: int, mx: int) -> Dict:
    return {
        "type": "minecraft:item",
        "name": item_name,
        "functions": [{"function": "minecraft:set_count", "count": {"min": mn, "max": mx}}],
    }


def build_house_loot_table(
    pistols: List[str],
    shotguns: List[str],
    rifles: List[str],
    ammo_stack: Dict[str, int],
    attachments: List[str],
    gun_to_ammo: Dict[str, str],
    gun_to_firemode: Dict[str, str],
    ak_id: Optional[str] = None,
) -> Dict:
    supplies_entries = [_vanilla_item_entry(e["name"], e["min"], e["max"]) for e in SUPPLIES_ENTRIES]
    resources_entries = [_vanilla_item_entry(e["name"], e["min"], e["max"]) for e in RESOURCES_ENTRIES]

    # --- Guns
    gun_entries: List[Dict] = []
    for g in pistols:
        fm = gun_to_firemode.get(g, DEFAULT_FIREMODE_PISTOL)
        gun_entries.append(gun_entry(g, fire_mode=fm, weight=WEIGHT_PISTOL))
    for g in shotguns:
        fm = gun_to_firemode.get(g, DEFAULT_FIREMODE_SHOTGUN)
        gun_entries.append(gun_entry(g, fire_mode=fm, weight=WEIGHT_SHOTGUN))
    for g in rifles:
        fm = gun_to_firemode.get(g, DEFAULT_FIREMODE_RIFLE)
        gun_entries.append(gun_entry(g, fire_mode=fm, weight=WEIGHT_RIFLE))

    # --- Ammo split: shotgun ammo vs general
    shotgun_ammo_ids = sorted({gun_to_ammo.get(g, "") for g in shotguns if gun_to_ammo.get(g, "")})
    other_ammo_ids = sorted(set(ammo_stack.keys()) - set(shotgun_ammo_ids))

    shotgun_ammo_entries: List[Dict] = []
    if ENABLE_SHOTGUN_AMMO_POOL:
        for ammo_id in shotgun_ammo_ids:
            stack = ammo_stack.get(ammo_id, AMMO_STACK_FALLBACK_IF_MISSING)
            shotgun_ammo_entries.append(ammo_entry(ammo_id, stack, weight=WEIGHT_AMMO_SHOTGUN))

    ammo_entries: List[Dict] = []
    for ammo_id in other_ammo_ids:
        ammo_entries.append(ammo_entry(ammo_id, ammo_stack.get(ammo_id, 60), weight=WEIGHT_AMMO_GENERAL))

    # --- Attachments
    att_entries = [attachment_entry(a, weight=WEIGHT_ATTACHMENT) for a in attachments]

    pools: List[Dict] = [
        {"rolls": {"min": ROLLS_SUPPLIES[0], "max": ROLLS_SUPPLIES[1]}, "entries": supplies_entries},
        {"rolls": {"min": ROLLS_RESOURCES[0], "max": ROLLS_RESOURCES[1]}, "entries": resources_entries},
        {"rolls": {"min": ROLLS_GUNS[0], "max": ROLLS_GUNS[1]}, "entries": gun_entries},
    ]

    if shotgun_ammo_entries:
        pools.append({"rolls": {"min": ROLLS_AMMO_SHOTGUN[0], "max": ROLLS_AMMO_SHOTGUN[1]}, "entries": shotgun_ammo_entries})

    if ammo_entries:
        pools.append({"rolls": {"min": ROLLS_AMMO_GENERAL[0], "max": ROLLS_AMMO_GENERAL[1]}, "entries": ammo_entries})

    pools.append({"rolls": {"min": ROLLS_ATTACHMENTS[0], "max": ROLLS_ATTACHMENTS[1]}, "entries": att_entries})

    if ak_id:
        pools.insert(2, {
            "rolls": 1,
            "entries": [gun_entry(ak_id, fire_mode=gun_to_firemode.get(ak_id, DEFAULT_FIREMODE_RIFLE), weight=1)]
        })

    return {"type": "minecraft:chest", "pools": pools}


def build_fill_function(
    base_x: int, y: int, z: int, houses: int, step_x: int,
    normal_table: str, ak_table: str, ak_house_index: int
) -> str:
    lines: List[str] = []
    for i in range(houses):
        x = base_x + i * step_x
        lines.append(f"setblock {x} {y} {z} minecraft:chest")
        table = ak_table if i == ak_house_index else normal_table
        lines.append(f'data merge block {x} {y} {z} {{LootTable:"{table}"}}')
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate Minecraft datapack from TaCZ summary.csv for loot chests.")
    ap.add_argument("--csv", required=True, help="Path to summary.csv (from your scan)")
    ap.add_argument("--out", required=True, help="Output datapack folder (will be created)")
    ap.add_argument("--namespace", default=DEFAULT_NAMESPACE, help=f"Datapack namespace (default: {DEFAULT_NAMESPACE})")

    # allow overriding staging row from CLI if needed
    ap.add_argument("--base-x", type=int, default=STAGING_BASE_X)
    ap.add_argument("--y", type=int, default=STAGING_Y)
    ap.add_argument("--z", type=int, default=STAGING_Z)
    ap.add_argument("--houses", type=int, default=STAGING_HOUSES)
    ap.add_argument("--step-x", type=int, default=STAGING_STEP_X)

    if ENABLE_DEST_CSV_OVERRIDE:
        ap.add_argument("--dest-csv", default="", help="Optional CSV with destination coords (x,y,z).")

    ap.add_argument("--ak-id", default=DEFAULT_AK_ID, help=f"Gun id to guarantee once (default: {DEFAULT_AK_ID})")
    ap.add_argument("--ak-house-index", type=int, default=DEFAULT_AK_HOUSE_INDEX,
                    help=f"0-based house index to contain guaranteed gun (default: {DEFAULT_AK_HOUSE_INDEX})")
    


    args = ap.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    out_root = Path(args.out).expanduser().resolve()
    ns = args.namespace.strip()

    # destinations
    dests = VILLAGE_CHEST_DESTS
    if ENABLE_DEST_CSV_OVERRIDE and getattr(args, "dest_csv", ""):
        loaded = load_destinations_csv(Path(args.dest_csv).expanduser().resolve())
        if loaded:
            dests = loaded

    guns_rows, ammo_stack, attachments, gun_to_ammo, gun_to_firemode = read_summary_csv(csv_path)
    pistols, shotguns, rifles = filter_simple_guns(guns_rows)

    if not pistols and not shotguns and not rifles:
        raise SystemExit("No simple guns found (pistol/shotgun/rifle) in summary.csv")

    ak_id = (args.ak_id or "").strip() or None

    # datapack structure
    pack_dir = out_root
    data_dir = pack_dir / "data" / ns
    functions_dir = data_dir / "functions"
    loot_dir = data_dir / "loot_tables" / "chests"
    pack_dir.mkdir(parents=True, exist_ok=True)

    write_json(pack_dir / "pack.mcmeta", {
        "pack": {"pack_format": PACK_FORMAT, "description": "LWI loot generator (auto)"}
    })

    normal_table_name = f"{ns}:chests/house"
    ak_table_name = f"{ns}:chests/house_ak"

    house_table = build_house_loot_table(
        pistols=pistols, shotguns=shotguns, rifles=rifles,
        ammo_stack=ammo_stack, attachments=attachments,
        gun_to_ammo=gun_to_ammo, gun_to_firemode=gun_to_firemode,
        ak_id=None
    )
    house_ak_table = build_house_loot_table(
        pistols=pistols, shotguns=shotguns, rifles=rifles,
        ammo_stack=ammo_stack, attachments=attachments,
        gun_to_ammo=gun_to_ammo, gun_to_firemode=gun_to_firemode,
        ak_id=ak_id
    )

    write_json(loot_dir / "house.json", house_table)
    write_json(loot_dir / "house_ak.json", house_ak_table)

    functions_dir.mkdir(parents=True, exist_ok=True)

    (functions_dir / "fill_village.mcfunction").write_text(
        build_fill_function(
            base_x=args.base_x, y=args.y, z=args.z,
            houses=args.houses, step_x=args.step_x,
            normal_table=normal_table_name,
            ak_table=ak_table_name,
            ak_house_index=args.ak_house_index
        ),
        encoding="utf-8",
    )

    (functions_dir / "update_chests.mcfunction").write_text(
        build_update_chests_function(
            base_x=args.base_x, y=args.y, z=args.z,
            houses=args.houses, step_x=args.step_x,
            dests=dests,
            dimension=STAGING_DIMENSION,
        ),
        encoding="utf-8",
    )

    
    if SPAWN_AROUND_CHESTS:
        spawn_text = build_spawn_mobs_function(
            chest_coords=dests,               # или VILLAGE_CHEST_DESTS
            mobs_per_chest=MOBS_PER_CHEST,
            rmin=SPAWN_RADIUS_MIN,
            rmax=SPAWN_RADIUS_MAX,
            dimension="minecraft:overworld",
        )
        (functions_dir / "spawn_mobs.mcfunction").write_text(spawn_text, encoding="utf-8")

    print("Datapack generated:", pack_dir)
    print("Functions to run in-game:")
    print(" - /function " + ns + ":fill_village")
    print(" - /function " + ns + ":update_chests")
    print("Loot tables:")
    print(" -", loot_dir / "house.json")
    print(" -", loot_dir / "house_ak.json")
    print(f"Destinations used: {min(args.houses, len(dests))} of {len(dests)} coords")


if __name__ == "__main__":
    main()
