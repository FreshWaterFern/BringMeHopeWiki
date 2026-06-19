#!/usr/bin/env python3
"""
One-time backfill: write a "<Display Name> - Version" row into the game's
Items.csv for every item, derived from when the item's script was first
committed.

Rule (set by the project owner):
  * item script first committed on/after 2026-06-15  -> 0.5.11  (this week)
  * anything older                                   -> 0.0.0

After this runs, Items.csv is the source of truth for item versions; the wiki
generator reads it from there. When adding a new item, add its
"<Name> - Version,<x.y.z>" row by hand alongside the name/description rows.

Run from the wiki repo root:  py tools/backfill_versions.py
Re-running is safe: items that already have a Version row are left untouched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_pages import (  # noqa: E402
    resolve_game_project,
    strip_comments,
    find_item_create_calls,
    split_args,
    unquote,
)

WEEK_START = "2026-06-15"
THIS_WEEK = "0.5.11"
OLDER = "0.0.0"


def git_add_date(repo_root: Path, relpath: str) -> str:
    """Date (YYYY-MM-DD) of the first commit to touch a file."""
    res = subprocess.run(
        ["git", "-C", str(repo_root), "log", "--reverse", "--format=%cs",
         "--", relpath],
        capture_output=True, text=True,
    )
    lines = res.stdout.splitlines()
    return lines[0] if lines else ""


def line_key(line: str) -> str:
    """The first CSV field (the lookup key) of a raw line."""
    if line.startswith('"'):
        m = re.match(r'"((?:[^"]|"")*)"', line)
        if m:
            return m.group(1).replace('""', '"')
    return line.split(",", 1)[0]


def main() -> None:
    game = resolve_game_project()
    repo_root = game.parent
    csv_path = game / "datafiles" / "Languages" / "English" / "Items.csv"

    # Display name -> version, from each script's git add-date.
    versions: dict[str, str] = {}
    for gml in sorted(game.glob("scripts/scr_itemdb_*/scr_itemdb_*.gml")):
        rel = gml.relative_to(repo_root).as_posix()
        date = git_add_date(repo_root, rel)
        ver = THIS_WEEK if date and date >= WEEK_START else OLDER
        text = strip_comments(gml.read_text(encoding="utf-8", errors="ignore"))
        for raw in find_item_create_calls(text):
            args = split_args(raw)
            if len(args) < 6:
                continue
            name = unquote(args[0])
            if name:
                versions[name] = ver

    raw_text = csv_path.read_text(encoding="utf-8-sig")
    newline = "\r\n" if "\r\n" in raw_text else "\n"
    lines = raw_text.splitlines()

    already = {
        line_key(ln)[: -len(" - Version")]
        for ln in lines
        if line_key(ln).endswith(" - Version")
    }

    out: list[str] = []
    inserted: set[str] = set()
    for ln in lines:
        out.append(ln)
        k = line_key(ln)
        if k in versions and k not in already and k not in inserted:
            keyfield = f'"{k} - Version"' if ln.startswith('"') else f"{k} - Version"
            out.append(f"{keyfield},{versions[k]}")
            inserted.add(k)

    missing = sorted(set(versions) - already - inserted)
    csv_path.write_text(newline.join(out) + newline, encoding="utf-8-sig")

    n_week = sum(1 for v in versions.values() if v == THIS_WEEK)
    print(f"items classified: {len(versions)} "
          f"({n_week} this week / {len(versions) - n_week} older)")
    print(f"version rows inserted: {len(inserted)}")
    if already:
        print(f"left untouched (already had a row): {len(already)}")
    if missing:
        print("WARNING: no CSV name row found for: " + ", ".join(missing))


if __name__ == "__main__":
    main()
