# Contributing to the Bring Me Hope Wiki

Thanks for helping document the game! All edits go through pull requests that a
maintainer reviews and merges.

## The easy way (in your browser)

1. Open the page you want to improve on the
   [live wiki](https://freshwaterfern.github.io/BringMeHopeWiki/).
2. Click the **edit pencil** in the top-right.
3. GitHub forks the repo for you and opens the Markdown editor.
4. Make your change, then **Propose changes** → **Create pull request**.

A maintainer will review it. Once merged, the live site updates automatically in
a minute or two.

## What you can edit

- ✅ The **Strategy & Notes** section on any item page: tips, synergies, builds,
  lore.
- ✅ Level pages: maps, enemies, secrets, where items are found.
- ✅ Fixing typos and wording anywhere.

## What not to touch

Anything between these markers is **generated from the game's source** and will be
overwritten:

```
<!-- AUTOGEN:START ... -->
   ...item stats, icon, in-game description...
<!-- AUTOGEN:END -->
```

If a stat in an AUTOGEN block looks wrong, **open an issue** instead of editing it
because it means the generator or the game data needs a fix.

## Style

- One item or area per page.
- Keep it spoiler-aware where it makes sense (use admonitions for big spoilers).
- Prefer plain language; this is for players.
