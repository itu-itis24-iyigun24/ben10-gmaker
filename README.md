# ben10-gmaker

**Documentation and tools for the level format used by the Ben 10 Flash collection games.**

These games — *Ben 10 Omniverse Collection* and *Ben 10 Omniverse: Galactic Monsters
Collection*, built by the French studio Yamago for Cartoon
Network — store their levels as plain XML files on disk. Nothing stopped anyone from
writing new ones, except that the format was never documented anywhere.

Now it is. This repo contains:

| | |
|---|---|
| [`docs/level-format.md`](docs/level-format.md) | The complete XML level format |
| [`docs/engine-notes.md`](docs/engine-notes.md) | Engine internals, physics constants, per-alien abilities, unused content |
| [`docs/running-locally.md`](docs/running-locally.md) | Getting a game to load your levels, and the traps along the way |
| [`docs/games.md`](docs/games.md) | Per-game specifics: aliens, slots, file naming |
| [`docs/preservation.md`](docs/preservation.md) | How well these games survive in public archives, and where the gaps are |
| [`editor/index.html`](editor/index.html) | A grid level editor — single file, no dependencies, no build step |
| [`tools/`](tools/) | Python generator, validator, and the extracted class inventory |
| [`levels/`](levels/) | Example levels made with the above |

---

## This repository contains no game files

The games belong to Cartoon Network / Turner; the engine to Yamago. Nothing here is theirs —
no SWFs, no sprites, no audio, no decompiled source dumps. What is here is a description of
a file format, tools written from scratch, and level files that are original work.

To actually play anything, get the games from
**[Flashpoint Archive](https://flashpointarchive.org/)**, the Flash preservation project.
[`docs/running-locally.md`](docs/running-locally.md) explains what to do from there.

---

## Quick start

**Draw a level.** Open `editor/index.html` in a browser. Pick the game, alien, slot,
objective and theme; paint the map; the XML updates live and the panel tells you the exact
filename to save it as. The editor works out wall autotiling, depths and bounding boxes for
you, and checks the level for the mistakes that break things.

**Or generate one.**

```python
from tools.genlevel import Level

L = Level(bg="BG_city_1", goal_id=2, char_id=1, wall_theme="ville")
for i in range(20):
    L.wall(i, 12); L.wall(i, 13)          # floor
L.platform(6, 10); L.platform(7, 10)      # a ledge
L.item(6, 9)                              # an orb on it
L.robot(12, 11, moving=True)
L.player(1, 11)
L.goal(18, 11)

open("swampfire_easy.xml", "w").write(L.xml())
```

**Then check it.**

```
python tools/validate.py swampfire_easy.xml --game omniverse
```

**Then play it.** Drop the file in the game's `save/` folder and launch. See
[`docs/running-locally.md`](docs/running-locally.md).

---

## The one rule that will bite you

Do not write `<data><variant>` into a cell. The engine reads a missing variant as "pick one
yourself" and chooses a valid sprite state at random; an explicit value is an index that
must exist on that specific sprite, and a wrong guess is a hard `TypeError #1009` crash.

The full explanation, with the engine source that proves it, is in
[level-format.md §11](docs/level-format.md#11-the-variant-rule). Both tools here already
follow the rule.

---

## What this is not

The validator checks that a level is **well-formed** — valid classes, no overlapping
objects, no enemy on the spawn, objective consistent with contents. It does **not** check
that a level is **beatable**.

That turns out to be genuinely hard here, and it is worth saying why: the aliens traverse
very differently. Big Chill glides, Blitzwolfer double-jumps, Bloxx builds his own platforms
mid-level, Cannonbolt and Jetray smash through obstacles others cannot pass. A static
reachability analysis calibrated against the original levels still reports some of them as
unbeatable — so it would report false failures on yours too. Playtest your levels.

---

## How this was worked out

The games' ActionScript 3 was decompiled with
[JPEXS Free Flash Decompiler](https://github.com/jindrapetrik/jpexs-decompiler), and every
claim in the docs was checked against the ten original level files that ship with the games.
Where a rule comes from the engine source, the docs quote it. The class inventory in
`tools/class-inventory.json` is generated straight from the games' sprite libraries with
`ffdec -dumpAS3`.

## Contributing

Useful things, roughly in order of value:

- **A third game.** If another Yamago/Cartoon Network title uses this format, its class
  inventory and any format differences would be worth adding.
- **English strings for the editor.** Its UI is currently Turkish.
- **Levels.** `levels/` takes new sets; say which alien and slot each is for.
- **Corrections.** If something in the docs is wrong, an issue with the decompiled source to
  back it up is very welcome.

## License

MIT — see [LICENSE](LICENSE). Applies to the documentation, the tools and the editor. It
does not and cannot apply to the games themselves.
