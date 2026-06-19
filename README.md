# Bring Me Hope Wiki

Source for the [Bring Me Hope wiki](https://freshwaterfern.github.io/Bring-Me-Hope-Wiki/),
built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and
published free on GitHub Pages.

## How it's organised

- `docs/` — the wiki content (Markdown). This is what contributors edit.
- `tools/generate_pages.py` — generates item & level pages from the **private**
  game source. Maintainers run this when items change.
- `mkdocs.yml` — site configuration and theme.
- `.github/workflows/deploy.yml` — builds and deploys to GitHub Pages on every
  push to `main`.

### Edit-safe generation

Generated pages wrap their data in an `<!-- AUTOGEN -->` block. Re-running the
generator only replaces that block — the community-written **Strategy & Notes**
sections are preserved.

## Maintainers: regenerating item pages

Requires a local checkout of the private game repo next to this one
(`../Bring-Me-Hope-Game-/`), or set `BMH_GAME_PROJECT` to the `Bring Me Hope`
project folder.

```sh
py tools/generate_pages.py          # regenerate items + levels + icons
py tools/generate_pages.py --no-icons
```

Then commit the changes under `docs/`.

## Building locally

```sh
py -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
mkdocs serve                     # live preview at http://127.0.0.1:8000
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
