<!-- Hand-written page. The generator does not touch this file, so it is safe across redeploys. -->

# Level persistence

When you leave a room and come back, the game remembers most of what you did there. The
room's state is saved the moment you leave and restored when you return. It is also
written into your save file, so those changes survive even after you quit and reload.

## What stays when you leave

- **Destroyed and modified props.** Broken pots, smashed crates, and other destructibles
  stay broken or stay in their changed state.
- **Floor decals.** Blood splatter, scorch and burn marks, footprints, and spent bullet
  and shotgun shells remain on the ground.
- **Spilled fluids.** Any water, oil, poison, or ice you created stays where you left it.
  See [Fluids](fluids.md).
- **Things you collected.** Items you already picked up stay gone, opened chests stay
  opened, and collected key items stay collected.
- **Burnt or destroyed foliage.** Grass and similar plants remember if they were burnt.

## What does not stay

- **Dropped items.** Any item lying loose on the ground disappears once you leave the
  room, so grab what you want before you go. This is deliberate: the game does not
  re-create dropped items when you return.
- **Rooms flagged to reset.** Some rooms are tagged to never persist (arenas, cutscene
  rooms, and similar). These reset to their original layout every time you enter.

## Examples of things that persist

| Thing | What it remembers |
|---|---|
| Grass (`par_grass`) | Whether it was burnt. |
| Breakable props (`par_breakable`) | Whether it was broken. |
| Destructibles (`obj_destructible`) | Its changed sprite and state. |
| Placed items (`obj_prop_item`) | Whether it was taken. |
| Chests (`obj_prop_item_chest`) | Whether they were opened. |
| Floor decals | Blood, burns, footprints, and shells. |
| Spilled fluids | The full fluid layout of the room. |

## How it works under the hood

Each room keeps a small "room data" record with a few parts:

- **Modified room objects**, such as grass and breakables, each storing a tiny bit of
  state (grass stores whether it is burnt, breakables store whether they are broken).
- **Extra spawned objects**, such as chests and destructibles, which are re-created from
  the record when you return.
- **The fluid grid**, a snapshot of every fluid tile in the room.
- **The floor decals**, baked into a buffer and stored with the room.

When you leave a room, its current state is snapshotted in memory. When you save the
game, those snapshots are written to disk, one file per room, and returning to a room
restores it. Objects that persist register themselves on room start and remove
themselves if their saved state says they were destroyed.

Dropped items are the one thing the loader skips on purpose, which is why they vanish
when you leave. Rooms tagged `no_persist` opt out of all of this and always reset to
their original layout.
