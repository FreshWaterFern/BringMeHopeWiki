#!/usr/bin/env python3
"""
Bring Me Hope wiki page generator.

Parses the (private) GameMaker game source and emits Markdown pages for the
(public) MkDocs wiki:

  * one page per item, built from `scr_itemdb_<key>.gml` + Items.csv + the
    item's sprite icon, split into Items / Key Items / Special Items
  * a sortable index table per category (the version comes from Items.csv)
  * a scaffolded level index grouped by area

Edit safety
-----------
Each generated page wraps its data in an AUTOGEN block:

    <!-- AUTOGEN:START ... -->
    ...stats, icon, in-game description...
    <!-- AUTOGEN:END -->

Only the content *between* those markers is regenerated. Anything outside the
block (notably the community-written "Strategy & Notes" section) is preserved
across runs, so re-running this after adding items never clobbers contributions.

Usage
-----
    py tools/generate_pages.py
    py tools/generate_pages.py --no-icons      # skip sprite export

The path to the game project is resolved from (in order):
  1. env var BMH_GAME_PROJECT
  2. ../../Bring-Me-Hope-Game-/Bring Me Hope   (sibling checkout default)
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

WIKI_ROOT = Path(__file__).resolve().parent.parent
DOCS = WIKI_ROOT / "docs"


def resolve_game_project() -> Path:
    env = os.environ.get("BMH_GAME_PROJECT")
    if env:
        p = Path(env).expanduser().resolve()
    else:
        p = (WIKI_ROOT.parent / "Bring-Me-Hope-Game-" / "Bring Me Hope").resolve()
    if not (p / "scripts").is_dir():
        sys.exit(
            f"Game project not found at:\n  {p}\n"
            "Set BMH_GAME_PROJECT to the 'Bring Me Hope' project folder "
            "(the one containing scripts/, datafiles/, sprites/)."
        )
    return p


# --------------------------------------------------------------------------- #
# AUTOGEN block handling
# --------------------------------------------------------------------------- #

AUTOGEN_START = "<!-- AUTOGEN:START (regenerated from game source; edits inside this block are overwritten on the next run) -->"
AUTOGEN_END = "<!-- AUTOGEN:END -->"
_AUTOGEN_RE = re.compile(
    re.escape("<!-- AUTOGEN:START") + r".*?" + re.escape(AUTOGEN_END),
    re.DOTALL,
)


def write_with_autogen(path: Path, new_block: str, new_file_template) -> None:
    """Create or update a page, replacing only its AUTOGEN region."""
    region = f"{AUTOGEN_START}\n{new_block.strip()}\n{AUTOGEN_END}"
    if path.exists():
        original = path.read_text(encoding="utf-8")
        if _AUTOGEN_RE.search(original):
            updated = _AUTOGEN_RE.sub(lambda _: region, original, count=1)
        else:
            # No marker (hand-created page): prepend a fresh region.
            updated = region + "\n\n" + original
        if updated != original:
            path.write_text(updated, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_file_template(region), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Parsing item_create(...) out of GML
# --------------------------------------------------------------------------- #

def split_args(s: str) -> list[str]:
    """Split a call's argument list on top-level commas (quote/paren aware)."""
    args, depth, quote, buf = [], 0, None, []
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        args.append("".join(buf).strip())
    return args


def strip_comments(text: str) -> str:
    """Remove // and /* */ comments (string-literal aware) so we never parse
    commented-out item_create calls."""
    out, i, n, quote = [], 0, len(text), None
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            i += 1
        elif ch in "\"'":
            quote = ch
            out.append(ch)
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def find_item_create_calls(text: str) -> list[str]:
    """Return the raw argument strings of every item_create(...) call."""
    calls = []
    for m in re.finditer(r"item_create\s*\(", text):
        i = m.end()
        depth, quote, start = 1, None, i
        while i < len(text) and depth:
            ch = text[i]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        calls.append(text[start : i - 1])
    return calls


def unquote(token: str) -> str | None:
    token = token.strip()
    if len(token) >= 2 and token[0] in "\"'" and token[-1] == token[0]:
        return token[1:-1]
    return None


def parse_item(gml_text: str):
    """Yield item dicts from one item-db script (handles multi-create files).

    Signature: item_create(name, save_id, price, sprite, stack, grade,
                           is_key=false, body_part=BodyPart.Chest, ...)
    The last two are optional, so 6 args is the minimum.
    """
    for raw in find_item_create_calls(strip_comments(gml_text)):
        args = split_args(raw)
        if len(args) < 6:
            continue
        name = unquote(args[0])
        key = unquote(args[1])
        if name is None or key is None:
            # Non-literal (e.g. a loop building keys); skip and document by hand.
            continue
        price_raw = args[2].strip()
        try:
            price = int(re.sub(r"[_\s]", "", price_raw))
        except ValueError:
            price = price_raw  # keep expression as-is
        grade = args[5].split(".")[-1].strip()
        is_key = len(args) > 6 and args[6].strip().lower() == "true"
        slot = args[7].split(".")[-1].strip() if len(args) > 7 else "Chest"
        # add_to_loottable defaults to true; only an explicit `false` removes it.
        add_to_loot = args[8].strip().lower() != "false" if len(args) > 8 else True
        try:
            stack = int(args[4].strip())
        except ValueError:
            stack = args[4].strip()
        yield {
            "name": name,
            "key": key,
            "price": price,
            "sprite": args[3].strip(),
            "stack": stack,
            "grade": grade,
            "is_key": is_key,
            "slot": slot,
            "add_to_loot": add_to_loot,
        }


# --------------------------------------------------------------------------- #
# Items.csv  (name -> text, "<name> - Desc" -> description)
# --------------------------------------------------------------------------- #

def load_csv(path: Path) -> dict[str, str]:
    table: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                table[row[0].strip()] = row[1].strip()
    return table


# --------------------------------------------------------------------------- #
# Icons
# --------------------------------------------------------------------------- #

_FRAME_RE = re.compile(r'"frames"\s*:\s*\[\s*\{[^}]*?"name"\s*:\s*"([0-9a-fA-F-]+)"')


def export_icon(game: Path, sprite_name: str, key: str, out_dir: Path) -> bool:
    sprite_dir = game / "sprites" / sprite_name
    if not sprite_dir.is_dir():
        return False
    src = None
    yy = sprite_dir / f"{sprite_name}.yy"
    if yy.exists():
        m = _FRAME_RE.search(yy.read_text(encoding="utf-8", errors="ignore"))
        if m:
            cand = sprite_dir / f"{m.group(1)}.png"
            if cand.exists():
                src = cand
    if src is None:  # fall back to first PNG in the folder (not in layers/)
        pngs = sorted(p for p in sprite_dir.glob("*.png"))
        if pngs:
            src = pngs[0]
    if src is None:
        return False
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / f"{key}.png")
    return True


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

GRADE_ORDER = ["Ordinary", "Striking", "Remarkable", "Exceptional",
               "Exotic", "Chaos", "Key"]


def grade_span(grade: str) -> str:
    cls = "grade-" + re.sub(r"[^a-z]", "", grade.lower())
    return f'<span class="grade {cls}">{grade}</span>'


# Item categories -> (folder, page title, index blurb). The folder names are
# chosen so MkDocs auto-nav titles them nicely (e.g. key-items -> "Key Items").
CATEGORIES = {
    "regular": (
        "items", "Items",
        "Items you can find in the loot pool.",
    ),
    "key": (
        "key-items", "Key Items",
        "Quest and key items used to progress. These are not part of the loot pool.",
    ),
    "special": (
        "special-items", "Special Items",
        "Items that are not found in the loot pool; they are obtained through other means.",
    ),
}


def category_of(it: dict) -> str:
    if it["is_key"]:
        return "key"
    if not it["add_to_loot"]:
        return "special"
    return "regular"


def item_block(it: dict, desc: str, has_icon: bool) -> str:
    lines = []
    if has_icon:
        lines.append(f'![{it["name"]}](../assets/icons/{it["key"]}.png){{ .item-icon }}\n')
    lines.append("| Property | Value |")
    lines.append("|---|---|")
    lines.append(f'| Grade | {grade_span(it["grade"])} |')
    if not it["is_key"]:
        lines.append(f'| Equip slot | {it["slot"]} |')
    lines.append(f'| Max stack | {it["stack"]} |')
    lines.append(f'| Added in version | {it["version"]} |')
    lines.append(f'| Save id | `{it["key"]}` |')
    body = "\n".join(lines)
    if desc:
        body += f"\n\n**In-game description:** {desc}"
    if it["category"] == "special":
        body += "\n\n_Not found in the loot pool; obtained through other means._"
    return body


def item_template(name: str):
    def make(region: str) -> str:
        return (
            f"# {name}\n\n"
            f"{region}\n\n"
            "## Strategy & Notes\n\n"
            "_Community-maintained: add tips, synergies, build ideas, and lore here._\n"
        )
    return make


# --------------------------------------------------------------------------- #
# Levels (scaffold; rooms have no rich metadata, so this is community-seeded)
# --------------------------------------------------------------------------- #

SKIP_ROOM = re.compile(
    r"^(rm_)?(battle|dummy|editor|props|npc_test|opening|gameintro|"
    r"praesidio_trailer)$"
)

AREA_LABELS = {
    "abandonedtown": "Abandoned Town",
    "crystalsubway": "Crystal Subway",
    "frostedcaves": "Frosted Caves",
    "seaelevatorstation": "Sea Elevator Station",
    "sandcity": "Sand City",
    "beyond": "Beyond",
    "guppo": "Guppo",
    "bebeshouse": "Bebe's House",
    "forest": "Forest",
    "intro": "Intro / Hub",
}


def area_for(room: str) -> str:
    name = room[3:] if room.startswith("rm_") else room
    for token, label in AREA_LABELS.items():
        if token in name:
            return label
    return "Other"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-icons", action="store_true", help="skip sprite export")
    args = ap.parse_args()

    game = resolve_game_project()
    csv_path = game / "datafiles" / "Languages" / "English" / "Items.csv"
    text = load_csv(csv_path) if csv_path.exists() else {}

    icons_dir = DOCS / "assets" / "icons"
    by_cat: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    total = 0
    skipped: list[str] = []

    for gml in sorted(game.glob("scripts/scr_itemdb_*/scr_itemdb_*.gml")):
        parsed = list(parse_item(gml.read_text(encoding="utf-8", errors="ignore")))
        if not parsed:
            skipped.append(gml.parent.name)
            continue
        for it in parsed:
            it["category"] = category_of(it)
            it["version"] = text.get(f'{it["name"]} - Version', "Unknown")
            desc = text.get(f'{it["name"]} - Desc', "")
            folder = CATEGORIES[it["category"]][0]
            has_icon = (not args.no_icons) and export_icon(
                game, it["sprite"], it["key"], icons_dir
            )
            it["_desc"] = desc
            it["_icon"] = has_icon
            write_with_autogen(
                DOCS / folder / f'{it["key"]}.md',
                item_block(it, desc, has_icon),
                item_template(it["name"]),
            )
            by_cat[it["category"]].append(it)
            total += 1

    for cat, (folder, title, blurb) in CATEGORIES.items():
        rows = sorted(by_cat[cat], key=lambda it: it["name"].lower())
        write_category_index(DOCS / folder / "index.md", title, blurb, rows)
    write_levels(game)

    print(f"items: {total} pages "
          f"(regular {len(by_cat['regular'])}, "
          f"key {len(by_cat['key'])}, special {len(by_cat['special'])})")
    print(f"icons: {sum(1 for c in by_cat.values() for it in c if it['_icon'])} exported")
    if skipped:
        print(f"skipped (no literal item_create): {', '.join(skipped)}")


def write_category_index(path: Path, title: str, blurb: str,
                         items: list[dict]) -> None:
    rows = [f"# {title}", "",
            f"{blurb} {len(items)} in total. Click a column header to sort, "
            "or click an item name for its full page.", "",
            "| Icon | Name | Grade | Slot | Version | Description |",
            "|---|---|---|---|---|---|"]
    for it in items:
        icon = (f'![](../assets/icons/{it["key"]}.png){{ .item-icon-sm }}'
                if it["_icon"] else "")
        name = f'[{it["name"]}]({it["key"]}.md)'
        slot_display = "N/A" if it["is_key"] else it["slot"]
        rows.append(
            f'| {icon} | {name} | {grade_span(it["grade"])} | {slot_display} '
            f'| {it["version"]} | {it["_desc"]} |'
        )
    block = "\n".join(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{AUTOGEN_START}\n{block}\n{AUTOGEN_END}\n", encoding="utf-8"
    )


def write_levels(game: Path) -> None:
    rooms = sorted(p.name for p in (game / "rooms").iterdir() if p.is_dir())
    by_area: dict[str, list[str]] = {}
    for r in rooms:
        if SKIP_ROOM.match(r):
            continue
        by_area.setdefault(area_for(r), []).append(r)

    out = ["# Levels", "",
           "Areas of *Bring Me Hope*, grouped from the game's rooms. "
           "These are seeded automatically; flesh out each area below with "
           "maps, enemies, secrets, and items found there.", ""]
    for area in sorted(by_area):
        out.append(f"## {area}")
        out.append("")
        out.append("Rooms:")
        out.append("")
        for r in by_area[area]:
            out.append(f"- `{r}`")
        out.append("")
    block = "\n".join(out).rstrip()
    (DOCS / "levels").mkdir(parents=True, exist_ok=True)
    write_with_autogen(
        DOCS / "levels" / "index.md",
        block,
        lambda region: region + "\n",
    )


if __name__ == "__main__":
    main()
