# 🌱 Bring Me Hope Wiki

**[📖 Read the wiki → freshwaterfern.github.io/BringMeHopeWiki](https://freshwaterfern.github.io/BringMeHopeWiki/)**

Welcome, adventurer! This is the community wiki for **Bring Me Hope**, your guide
to every item, area, and secret in the game. Whether you're chasing the perfect
build, hunting down a quest key, or just curious what that shiny thing does, you'll
find it here.

## What's inside

- **🎒 [Items](https://freshwaterfern.github.io/BringMeHopeWiki/items/)**: everything in
  the loot pool, with grade, equip slot, the version it was added in, and what it does.
  Sort any table column to compare.
- **🔑 [Key Items](https://freshwaterfern.github.io/BringMeHopeWiki/key-items/)**: quest
  and key items used to progress.
- **⭐ [Special Items](https://freshwaterfern.github.io/BringMeHopeWiki/special-items/)**:
  items not found in the loot pool, obtained through other means.
- **🗺️ [Levels](https://freshwaterfern.github.io/BringMeHopeWiki/levels/)**: the areas
  of the world, their rooms, enemies, and the loot hiding in them.

## ✏️ Help build the wiki

This wiki is made by players, for players, and **you're welcome to pitch in** with
no coding required:

1. Find a page that's missing tips, lore, or strategy on the
   [live wiki](https://freshwaterfern.github.io/BringMeHopeWiki/).
2. Click the **pencil icon** in the top-right of the page.
3. Make your edit and hit **Propose changes**. GitHub walks you through the rest.

A maintainer reviews every suggestion before it goes live, so don't worry about
breaking anything. Add your favourite synergies, build ideas, boss strategies, or
bits of lore. Every contribution helps the next player.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide, including what *not* to
edit (the item stat boxes are generated automatically and always match the live
game).

## 🐛 Found a mistake?

If an item's stats look wrong, or something's out of date, please
[open an issue](https://github.com/FreshWaterFern/BringMeHopeWiki/issues). That's the
fastest way to get it fixed.

---

## 🛠️ For maintainers & developers

This site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
and published free on GitHub Pages.

**Repository layout**

- `docs/`: the wiki content (Markdown). This is what contributors edit.
- `tools/generate_pages.py`: generates item & level pages from the **private** game
  source. Run this when items change.
- `mkdocs.yml`: site configuration and theme.
- `.github/workflows/deploy.yml`: builds and deploys to GitHub Pages on every push
  to `main`.

**Edit-safe generation.** Generated pages wrap their data in an `<!-- AUTOGEN -->`
block. Re-running the generator only replaces that block, so the community-written
**Strategy & Notes** sections are always preserved.

**Regenerating item pages.** Requires a local checkout of the private game repo next
to this one (`../Bring-Me-Hope-Game-/`), or set `BMH_GAME_PROJECT` to the
`Bring Me Hope` project folder.

```sh
py tools/generate_pages.py          # regenerate items + levels + icons
py tools/generate_pages.py --no-icons
```

Then commit the changes under `docs/`.

**Previewing locally.**

```sh
py -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
mkdocs serve                     # live preview at http://127.0.0.1:8000
```
