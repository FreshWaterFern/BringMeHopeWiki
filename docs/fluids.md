<!-- Hand-written page. The generator does not touch this file, so it is safe across redeploys. -->

# Fluids

Fluids are liquids that sit on the floor of a room. Standing in a fluid applies its
effect every frame you remain in it, and a status word pops above your head when an
effect first lands. Anything with fluid immunity ignores all of them.

These are the fluids defined in the game (the `FluidData` enum). `Blocked`, `Empty`,
and `Size` are internal markers, not real fluids.

!!! warning "Not in the game yet"
    **Ghoul Broth**, **Frozen Oil**, and the six **Paints** are defined in the game's
    code but currently have no working way to be created, so you will not run into them
    in normal play yet. They are documented here for completeness.

## Effects at a glance

| Fluid | What it does to you |
|---|---|
| **Water** | Makes you **Wet** for about 2 seconds. While wet, fire is put out and you can be frozen. |
| **Ice** | Very slippery (friction x0.3). Puts fire out. **Freezes** you if you are Wet. |
| **Oil** | Slightly slippery (friction x0.8). Coats you in **Oil**, which is flammable. |
| **Frozen Oil** _(not in the game yet)_ | Extremely slippery (friction x0.2). **Freezes** you if you are Wet. |
| **Poison** | **Poisons** you (damage over time). |
| **Ghoul Broth** _(not in the game yet)_ | **Heals** you: grants health regeneration while you stand in it. Flammable. |
| **Paint** (Blue, Red, Yellow, Green, Purple, Orange) _(not in the game yet)_ | **Slows** your movement by 30%. The six colors behave the same in combat. |

## How fluids interact

- **Water and fire**: water puts fire out, and standing in water or ice douses you if you are burning.
- **Wet plus Ice or Frozen Oil**: being Wet and then touching ice or frozen oil **freezes** you.
- **Oil and fire**: oil is flammable. Fire and explosions ignite oil (and frozen oil and ghoul broth), turning it into fire.
- **Soul of Ice**: this effect freezes Water into Ice and Oil into Frozen Oil.
- **Orb of Absorption** ([item](items/orbofabsorption.md)): the opposite of a creator. It soaks up any fluid in a 3 by 3 area around you.

## What creates each fluid

Item names link to their wiki page. Object names are the in-game object ids (enemies,
bosses, and breakable props), which do not have their own pages yet.

### Water
- **Items**: [Water Bubble](items/waterbubble.md) (leaves a trail while dashing), [Super Barrel](items/superbarrel.md) (random barrels while dashing).
- **Objects**: Ice Betafish Wizard (`obj_betafish_wizard_ice`), Guppo ice spikes (`obj_guppo_icespike_0/1/3`), sea cave water pots, Sea Cave City water buckets, Sand City water jars, and water fluid props (`obj_prop_fluid_water_3x3`).

### Oil
- **Items**: [Slicked Boot](items/slickedboot.md) (leaves a trail while dashing), [Super Barrel](items/superbarrel.md) (random).
- **Objects**: sea cave oil pots, Sand City oil jars.

### Poison
- **Items**: [Super Barrel](items/superbarrel.md) (random).
- **Objects**: Scooter Slug (`obj_scooterslug`), sea cave poison pots.

### Ice
- **Items**: none directly (ice is made by freezing water).
- **Objects**: Ice Slug (`obj_iceslug`), the Soul of Ice effect freezing water (`obj_effect_soulofice`), frosted grass (`par_grass`), and ice fluid props (`obj_prop_fluid_ice_3x3`).

### Frozen Oil
_Not in the game yet._ Frozen Oil exists in the code (it is oil that has been frozen),
but there is currently no working way to create it in game. The freezing logic lives in
`obj_effect_soulofice`.

### Ghoul Broth
_Not in the game yet._ Ghoul Broth exists in the code but currently has no working way to
be created in game.

### Paints (Blue, Red, Yellow, Green, Purple, Orange)
_Not in the game yet._ The six paints exist in the code but currently have no working way
to be created in game.

## Resisting fluids

Several items let you ignore a fluid's effect:

- [Holey Shoe](items/holeyshoe.md): immune to **Wet**, so Water does nothing to you.
- [Knitted Mitten](items/knittedmitten.md): immune to **Freezing**, which counters Ice and Frozen Oil.
- [Breathing Mask](items/breathingmask.md): immune to **Poison**.
- [Fire Mask](items/firemask.md): immune to **Burning**, which helps when oil ignites.

A full fluid immunity skips every effect on this page outright.

## Notes

- Generic fluid props (`obj_prop_fluid_1x1`, `obj_prop_fluid_water_3x3`, `obj_prop_fluid_ice_3x3`) place a configured fluid when triggered, so a level can spawn any fluid this way.
- Friction values above are multipliers on your normal grip: the lower the number, the more you slide. Frozen Oil (x0.2) is the most slippery surface in the game.
