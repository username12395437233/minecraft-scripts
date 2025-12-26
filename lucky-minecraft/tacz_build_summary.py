#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build summary.csv from TaCZ pack folders:
  <root>/index/ammo/*.json
  <root>/index/guns/*.json
  <root>/index/attachments/*.json
  <root>/data/guns/*.json (optional enrich)
  <root>/data/attachments/*.json (optional enrich)

It outputs CSV rows like:
  source,index,category,guns, index_id=tacz:glock_17, type=pistol, item_type=..., data_ref=...
  source,index,category,ammo, index_id=tacz:556x45, stack_size=60
  source,index,category,attachments, index_id=tacz:muzzle_compensator_trident, type=muzzle, ...

JSON in TaCZ often contains // and /* */ comments => we strip them.
If a file cannot be parsed or misses required fields, it is skipped (logged).
"""

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------
# JSON cleaning (comments, trailing commas)
# -----------------------------

_RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_RE_LINE_COMMENT = re.compile(r"(^|[^\:])//.*?$", re.MULTILINE)  # avoid matching "http://"
_RE_TRAILING_COMMA = re.compile(r",(\s*[\]}])")  # ,] or ,}

def load_json_relaxed(path: Path) -> Dict[str, Any]:
    """
    Load JSON that may contain // line comments, /* */ block comments, and trailing commas.
    Raises ValueError if cannot parse.
    """
    text = path.read_text(encoding="utf-8-sig", errors="strict")

    # strip block comments
    text = _RE_BLOCK_COMMENT.sub("", text)
    # strip line comments (but keep "http://")
    text = _RE_LINE_COMMENT.sub(r"\1", text)
    # remove trailing commas
    text = _RE_TRAILING_COMMA.sub(r"\1", text)

    try:
        return json.loads(text)
    except Exception as e:
        raise ValueError(f"JSON parse failed: {e}") from e


# -----------------------------
# Helpers
# -----------------------------

def ref_to_stem(ref: str) -> str:
    """
    "tacz:ak47_data" -> "ak47_data"
    "ak47_data" -> "ak47_data"
    "" -> ""
    """
    ref = (ref or "").strip()
    if not ref:
        return ""
    return ref.split(":", 1)[1] if ":" in ref else ref


def make_index_id(namespace: str, stem: str) -> str:
    """Filename stem -> tacz:<stem> (since Windows filenames can't include ':')."""
    stem = stem.strip()
    if not stem:
        return ""
    # if user passed something like "tacz_glock_17" and wants 그대로 — оставим как есть
    # но по умолчанию: namespace:stem
    if ":" in stem:
        return stem
    return f"{namespace}:{stem}"

def safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    v = d.get(key, default)
    return v

def find_data_file(data_root: Path, category: str, index_id: str) -> Optional[Path]:
    """
    Try to locate data JSON by:
      1) using stem of index_id (namespace:id) as filename
      2) allow subfolder by category: guns/ or attachments/
    """
    if ":" in index_id:
        stem = index_id.split(":", 1)[1]
    else:
        stem = index_id

    candidate = data_root / category / f"{stem}.json"
    return candidate if candidate.exists() else None


# -----------------------------
# Extractors
# -----------------------------

def scan_index_ammo(index_dir: Path, namespace: str, errors: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    ammo_dir = index_dir / "ammo"
    if not ammo_dir.exists():
        errors.append(f"Missing folder: {ammo_dir}")
        return rows

    for fp in sorted(ammo_dir.glob("*.json")):
        index_id = make_index_id(namespace, fp.stem)
        try:
            obj = load_json_relaxed(fp)
            stack_size = obj.get("stack_size", None)
            if stack_size is None:
                raise ValueError("missing required field: stack_size")

            # Some packs store stack_size as float/int/string
            try:
                stack_size_int = int(float(stack_size))
            except Exception:
                raise ValueError(f"bad stack_size: {stack_size!r}")

            rows.append({
                "source": "index",
                "category": "ammo",
                "index_id": index_id,
                "stack_size": stack_size_int,
                "name": safe_get(obj, "name", ""),
                "display": safe_get(obj, "display", ""),
                "file": str(fp),
            })
        except Exception as e:
            errors.append(f"[SKIP ammo] {fp.name}: {e}")
            continue

    return rows

def scan_index_guns(index_dir: Path, data_dir: Path, namespace: str, errors: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    guns_dir = index_dir / "guns"
    if not guns_dir.exists():
        errors.append(f"Missing folder: {guns_dir}")
        return rows

    for fp in sorted(guns_dir.glob("*.json")):
        index_id = make_index_id(namespace, fp.stem)
        try:
            obj = load_json_relaxed(fp)

            gtype = obj.get("type", None)
            if not gtype:
                raise ValueError("missing required field: type (pistol/shotgun/rifle/...)")

            row: Dict[str, Any] = {
                "source": "index",
                "category": "guns",
                "index_id": index_id,
                "type": str(gtype).lower(),
                "item_type": safe_get(obj, "item_type", ""),
                "sort": safe_get(obj, "sort", ""),
                "name": safe_get(obj, "name", ""),
                "display": safe_get(obj, "display", ""),
                "data_ref": safe_get(obj, "data", ""),
                "tooltip": safe_get(obj, "tooltip", ""),
                "file": str(fp),
            }

            # Enrich from data/guns/<id>.json if exists
            data_ref = safe_get(obj, "data", "")
            data_stem = ref_to_stem(data_ref)

            data_fp = (data_dir / "guns" / f"{data_stem}.json") if data_stem else None
            if data_fp and not data_fp.exists():
                data_fp = None  # не нашли — оставим без enrich

            if data_fp:
                try:
                    data_obj = load_json_relaxed(data_fp)
                    row["gun_ammo"] = safe_get(data_obj, "ammo", "")
                    row["ammo_amount"] = safe_get(data_obj, "ammo_amount", "")
                    row["weight"] = safe_get(data_obj, "weight", "")
                    row["rpm"] = safe_get(data_obj, "rpm", "")

                    fire_modes = safe_get(data_obj, "fire_mode", [])
                    if not isinstance(fire_modes, list):
                        fire_modes = []
                    # сохраним в CSV как "auto|semi|burst"
                    row["fire_mode"] = "|".join(str(x).lower() for x in fire_modes)

                    # выберем дефолт (логично: auto если есть, иначе semi, иначе первый)
                    fm = [str(x).lower() for x in fire_modes]
                    if "auto" in fm:
                        row["default_fire_mode"] = "AUTO"
                    elif "semi" in fm:
                        row["default_fire_mode"] = "SEMI"
                    elif "burst" in fm:
                        row["default_fire_mode"] = "BURST"
                    elif fm:
                        row["default_fire_mode"] = fm[0].upper()
                    else:
                        row["default_fire_mode"] = ""

                    bullet = data_obj.get("bullet", {}) if isinstance(data_obj.get("bullet", {}), dict) else {}
                    row["bullet_damage"] = safe_get(bullet, "damage", "")
                    row["bullet_speed"] = safe_get(bullet, "speed", "")
                    row["data_file"] = str(data_fp)
                except Exception as e:
                    errors.append(f"[WARN guns data] {data_fp.name}: {e}")

            rows.append(row)

        except Exception as e:
            errors.append(f"[SKIP guns] {fp.name}: {e}")
            continue

    return rows

def scan_index_attachments(index_dir: Path, data_dir: Path, namespace: str, errors: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    att_dir = index_dir / "attachments"
    if not att_dir.exists():
        errors.append(f"Missing folder: {att_dir}")
        return rows

    for fp in sorted(att_dir.glob("*.json")):
        index_id = make_index_id(namespace, fp.stem)
        try:
            obj = load_json_relaxed(fp)

            # type is very useful but sometimes may be absent
            att_type = safe_get(obj, "type", "")

            row: Dict[str, Any] = {
                "source": "index",
                "category": "attachments",
                "index_id": index_id,
                "type": str(att_type).lower() if att_type else "",
                "name": safe_get(obj, "name", ""),
                "display": safe_get(obj, "display", ""),
                "data_ref": safe_get(obj, "data", ""),
                "file": str(fp),
            }

            # Enrich from data/attachments/<id>.json if exists
            data_ref = safe_get(obj, "data", "")
            data_stem = ref_to_stem(data_ref)

            data_fp = (data_dir / "attachments" / f"{data_stem}.json") if data_stem else None
            if data_fp and not data_fp.exists():
                data_fp = None

            if data_fp:
                try:
                    data_obj = load_json_relaxed(data_fp)
                    row["weight"] = safe_get(data_obj, "weight", "")
                    row["extended_mag_level"] = safe_get(data_obj, "extended_mag_level", "")
                    row["data_file"] = str(data_fp)
                except Exception as e:
                    errors.append(f"[WARN attachments data] {data_fp.name}: {e}")

            rows.append(row)

        except Exception as e:
            errors.append(f"[SKIP attachments] {fp.name}: {e}")
            continue

    return rows


# -----------------------------
# CSV writer
# -----------------------------

def write_csv(out_csv: Path, rows: List[Dict[str, Any]]) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    # collect all keys for stable header
    keys: List[str] = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)

    # put the most important first (for your existing generator)
    preferred = ["source", "category", "index_id", "type", "stack_size"]
    header = preferred + [k for k in keys if k not in preferred]

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description="Build summary.csv from TaCZ index/data folders (relaxed JSON parsing).")
    ap.add_argument("--root", required=True,
                    help="Path to .../tacz_default_gun/data/tacz (contains index/ and data/)")
    ap.add_argument("--out", required=True, help="Output CSV path, e.g. D:/summary.csv")
    ap.add_argument("--namespace", default="tacz", help="Namespace prefix for ids (default: tacz)")
    ap.add_argument("--log", default="", help="Optional log file to write skipped files/warnings")

    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_csv = Path(args.out).expanduser().resolve()
    namespace = args.namespace.strip()

    index_dir = root / "index"
    data_dir = root / "data"

    errors: List[str] = []
    rows: List[Dict[str, Any]] = []

    rows += scan_index_ammo(index_dir, namespace, errors)
    rows += scan_index_guns(index_dir, data_dir, namespace, errors)
    rows += scan_index_attachments(index_dir, data_dir, namespace, errors)

    # de-dup by (source, category, index_id)
    uniq: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for r in rows:
        key = (str(r.get("source","")), str(r.get("category","")), str(r.get("index_id","")))
        uniq[key] = r
    rows = list(uniq.values())

    write_csv(out_csv, rows)

    # logging
    if args.log:
        log_path = Path(args.log).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("\n".join(errors) + ("\n" if errors else ""), encoding="utf-8")

    print("OK:", out_csv)
    print("Rows:", len(rows))
    if errors:
        print("Skipped/Warned:", len(errors))
        if not args.log:
            # show a few
            for line in errors[:15]:
                print(line)


if __name__ == "__main__":
    main()
