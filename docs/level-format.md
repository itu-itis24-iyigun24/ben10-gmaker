# The gmaker level format

Levels for the Ben 10 collection games are plain XML files. This document describes the
format completely enough to write a level by hand or generate one programmatically.

Everything here was recovered by decompiling the games' ActionScript 3 with
[JPEXS Free Flash Decompiler](https://github.com/jindrapetrik/jpexs-decompiler) and
cross-checking against the ten original level files that ship with the games. Class and
method names in the citations are the real ones from the decompiled source.

---

## 1. Where levels live

The engine builds the path itself, in `GameCreatorBen10Engine.getSelectedLevelDefaultUrl()`:

```actionscript
return (Config.mainPath == null ? "" : Config.mainPath + "/")
       + "save/" + this.idAlien + "_" + this.levelMode + ".xml";
```

So a level file is always `save/<alienId>_<slot>.xml`. What `<slot>` can be depends on the
game — see [games.md](games.md).

| Game | Slots | Example |
|---|---|---|
| Ben 10 Omniverse Collection | `easy`, `hard` | `save/swampfire_hard.xml` |
| Ben 10 Omniverse: Galactic Monsters | `0` … `4` | `save/snareoh_2.xml` |

---

## 2. Document skeleton

```xml
<level>
  <infos>
    <version>0.1.0</version>
  </infos>
  <tc>
    <id/>
    <title/>
  </tc>
  <game>
    <bg>
      <id>BG_city_1</id>
    </bg>
    <goal>
      <id>2</id>
    </goal>
    <character>
      <id>14</id>
    </character>
    <map>
      <!-- cells -->
    </map>
  </game>
</level>
```

| Element | Meaning |
|---|---|
| `infos/version` | Always `0.1.0` in every shipped level. Not validated. |
| `tc` | Title card. Empty in every shipped level; the engine tolerates it. |
| `game/bg/id` | Background class name, e.g. `BG_lava_0`. 18 exist. |
| `game/goal/id` | Objective type, `1`–`4`. See §6. |
| `game/character/id` | Which alien plays this level. See §7. |
| `game/map` | The cell list. |

### A second, unused format

`GameCreatorBen10Engine.onLoadXML()` has a branch for levels that are **not** story mode:

```actionscript
if (this.curMode == MODE_STORY) {
   this.levelXml = XML(pEvent.target.data);
} else {
   lbyte = Base64.decode(String(ltmpXml.game.levelData));
   lbyte.uncompress();
   this.levelXml = XML(lbyte.readObject());
}
```

Levels published through the game's (now dead) online gallery were stored as a
Base64'd, zlib-compressed `<levelData>` blob. Every level that ships on disk is the plain
story format described here — that is the one to write.

---

## 3. The grid

**20 columns × 14 rows.** `i` is the column (`0`–`19`, left to right), `j` is the row
(`0`–`13`, **top to bottom**). Row `13` is the bottom of the screen.

```
      i →  0                   19
   j  0   ┌────────────────────┐
      ↓   │                    │
          │                    │
     13   └────────────────────┘   ground usually sits at j=12,13
```

Every shipped level uses exactly this grid. There is no scrolling and no larger map.

---

## 4. Cell anatomy

```xml
<cell id="instance137529" i="5" j="9">
  <class>PF_0100</class>
  <depth>40000</depth>
  <rect>
    <imin>-1</imin><imax>1</imax>
    <jmin>-1</jmin><jmax>1</jmax>
  </rect>
  <dx>15</dx>
  <dy>15</dy>
</cell>
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Any unique string. The editor's own ids look like `instance137529`; nothing parses them. |
| `i`, `j` | yes | Grid position. |
| `class` | yes | Linkage name of a symbol in the game's sprite library. §5 and §8. |
| `depth` | yes | Draw order. §9. |
| `rect` | only for some classes | Bounding box in cells, relative to `i`,`j`. §10. |
| `dx`, `dy` | yes | Always `15` in every shipped cell. Sub-cell offset. |
| `data/variant` | **never write it** | §11 — this is the one rule that will crash your level. |

Cell order inside `<map>` does not matter to the engine; `depth` decides what draws on top.
Writing cells grouped by kind (walls first, player last) just makes the file readable.

---

## 5. Autotiling

Three families of class name encode their own connectivity. Compute the suffix from the
neighbours and you get the correct sprite with no manual work.

### Walls — `W_<theme>_URDL`

Four bits, in order **Up, Right, Down, Left**. `1` means "a wall of the same family is
there". All 16 combinations exist for every theme.

```
W_ville_0111   →  U=0 R=1 D=1 L=1   (open at the top: a floor surface)
W_ville_1101   →  U=1 R=1 D=0 L=1   (open at the bottom: a ceiling)
W_ville_1111   →  fully enclosed interior
W_ville_0000   →  isolated single block
```

This mapping was verified against all ten original levels: all four bits match neighbour
occupancy in 100% of cells.

**Themes.** Omniverse Collection: `ville`, `jungle`, `roche`, `lave`, `lave2`.
Galactic Monsters: `ville`, `jungle`, `roche`, `lave2`.
(`ville` is French for *town*; the engine was written by the French studio Yamago.)

### Platforms — `PF_0R0L`

Platforms connect **horizontally only**, so the up and down bits are always `0`. Only four
classes exist: `PF_0000`, `PF_0001`, `PF_0100`, `PF_0101`.

```
PF_0100  →  neighbour to the right    (left end of a strip)
PF_0101  →  neighbours both sides     (middle)
PF_0001  →  neighbour to the left     (right end)
PF_0000  →  standalone single platform
```

`PFall` is a separate class — a platform that falls away when stood on. It has no mask.

### Hazards — `W_saw_*`, `W_volt_*`

Saw blades and electric fields use the same four-bit name, but the original levels only
ever place them in **vertical runs**, so only the up/down bits are used:

```
W_saw_0010   →  top of a column
W_saw_1010   →  middle
W_saw_1000   →  bottom
W_saw_0000   →  single isolated hazard
```

All 16 masks exist in the library, but horizontal saw runs never appear in shipped content.

---

## 6. Objectives

`<goal><id>` picks the win condition, and the matching `Goal_*` class must be placed as a
cell — that cell is the exit door. The pairing comes from `DataMap.mapGoalTab`:

```actionscript
public static const mapGoalTab:Array =
   ["Goal_Neutral","Goal_Items","Goal_Enemies","Goal_EnemiesItems"];
```

| `<goal><id>` | Class to place | Objective (from `main_en.xml`) |
|---|---|---|
| `1` | `Goal_Neutral` | GET TO THE DOOR! |
| `2` | `Goal_Items` | COLLECT ALL ORBS! |
| `3` | `Goal_Enemies` | BATTLE ALL ENEMIES! |
| `4` | `Goal_EnemiesItems` | COLLECT ALL ORBS & BATTLE ALL ENEMIES! |

If the id says orbs must be collected, the level needs at least one `Item_*` cell — and
every one of them must be reachable, or the level cannot be finished. Same for enemies
with ids `3` and `4`.

---

## 7. Characters

`<character><id>` is a **1-based index** into `DataMap.mapCharTab`. From
`MyLvlMgr.getCharacterId()`:

```actionscript
return DataMap.mapCharTab[Number(_loc1_) - 1];
```

| id | Class | Alien | id | Class | Alien |
|---:|---|---|---:|---|---|
| 1 | `Ben10Swampfire` | Swampfire | 8 | `Ben10Cannonbolt` | Cannonbolt |
| 2 | `Ben10Humongousaur` | Humongousaur | 9 | `Ben10Echoecho` | Echo Echo |
| 3 | `Ben10Jetray` | Jetray | 10 | `Ben10Bigchill` | Big Chill |
| 4 | `Ben10Spidermonkey` | Spidermonkey | 11 | `Ben10Feedback` | Feedback |
| 5 | `Ben10Brainstorm` | Brainstorm | 12 | `Ben10Gravattack` | Gravattack |
| 6 | `Ben10Waterhazard` | Water Hazard | 13 | `Ben10BallWeevil` | Ball Weevil |
| 7 | `Ben10Terraspin` | Terraspin | 14 | `Ben10Bloxx` | Bloxx |

Galactic Monsters extends the table with `17` = `Ben10Blitzwolfer` and `18` = `Ben10SnareOh`.

The class named by the id must **also be placed as a cell** — that cell is the spawn point.
Both must agree; the id alone does not spawn anything.

Different aliens traverse very differently (double jump, glide, block-building), which
changes what a level can ask of the player. See [engine-notes.md](engine-notes.md).

---

## 8. Class catalogue

The full per-game list is in [`tools/class-inventory.json`](../tools/class-inventory.json),
generated from the games' own sprite libraries with `ffdec -dumpAS3`. Summary:

| Category | Classes | Notes |
|---|---|---|
| Walls | `W_<theme>_<URDL>` | 5 themes × 16 (Omniverse), 4 × 16 (Galactic Monsters) |
| Hazards | `W_saw_*`, `W_volt_*` | 16 masks each; lethal on contact |
| Platforms | `PF_0000/0001/0100/0101`, `PFall` | `PFall` collapses when stood on |
| Pass-through | `WallPhantom0`, `PFPhantom0`, `PFFall`, `PFFallWait` | used with `Item_phantom` |
| Orbs | `Item_city`, `Item_jungle`, `Item_lava`, `Item_phantom` | purely cosmetic variants |
| Enemies | `Robot_Fix`, `Robot_Move`, `Enemy_Generator` | `Robot_Move` patrols |
| Objects | `Object_box`, `Object_solidBox` | `Object_box` is pushable |
| Goals | `Goal_Neutral`, `Goal_Items`, `Goal_Enemies`, `Goal_EnemiesItems` | §6 |
| Players | `Ben10*` | §7 |
| Backgrounds | `BG_<theme>_<0-2>` | `city castle jungle landscape lava spaceship` |

A class that is not in the game's library simply does not draw — it will not crash. A class
that *is* there but is given a bad `variant` **will** crash; see §11.

---

## 9. Depth

`depth` is the draw order; higher is nearer the camera. Most kinds use a fixed value, so
there is little to think about:

| Kind | Depth |
|---|---|
| Walls | ~`19975`–`20019`, decreasing with `i` and with height |
| Hazards (`saw`, `volt`) | ~`29975`–`29993` |
| `PF_*` | `40000` |
| `WallPhantom0` | ~`44966`–`44996` |
| `PFall` | `50000` |
| `Goal_*` | `60000` |
| `Enemy_Generator` | `70000` |
| `Item_*` | `80000` |
| `Object_*` | `90000` |
| `Robot_*` | `100000` |
| `Ben10*` (player) | `110000` |

Only the wall band varies per cell, and since walls are opaque tiles that never overlap,
any consistent value inside the band works. The generator in this repo uses:

```python
depth = clamp(20019 - i - (13 - j), 19975, 20019)   # walls
depth = 29990 - j                                   # hazards
```

---

## 10. `rect`

Five classes carry a bounding box in cells, relative to the cell's own `i`,`j`:

| Class | `imin imax jmin jmax` | Meaning |
|---|---|---|
| `Goal_*` | `-2 2 -4 1` | the door occupies 5×6 cells |
| `Robot_Fix`, `Robot_Move` | `-1 1 -1 1` | 3×3 hitbox / patrol area |
| `Object_box`, `Object_solidBox` | `-1 1 -1 1` | 3×3 |

Every shipped level uses exactly these values. Nothing else takes a `rect`.

---

## 11. The `variant` rule

**Do not write `<data><variant>` at all.** This is the single most important rule in this
document; getting it wrong crashes the level with `TypeError #1009`.

Each sprite has a number of visual "states" — child sprites inside its MovieClip, counted at
runtime by `StateMgr.parse()`. `variant` selects one **by index**. From `Clip.build()`:

```actionscript
_loc2_ = cell.getData("variant");
if (_loc2_ == null) {
   variants = new StateMgr(_loc1_, -1);          // no variant → engine picks
   if (variants.length > 0) cell.setData("variant", variants.index);
} else {
   variants = new StateMgr(_loc1_, int(_loc2_)); // explicit index
}
```

and `StateMgr.setState()`:

```actionscript
if (statesByD.length > 0) {
   if (_loc2_ == -1) {
      _loc2_ = Math.round(Math.random() * (statesByD.length - 1));
   }
   curState = State(statesByD[_loc2_]);          // out of range → undefined → null
   genSpState();                                 // → #1009
```

So:

* **omitted** → the engine passes `-1` and picks a random valid state. Always safe, and you
  get free per-cell visual variety.
* **present** → you are asserting that this exact index exists on this exact sprite. Different
  sprites have different state counts, and they differ between the two games. Guessing wrong
  is a hard crash.

The shipped levels do write variants, because the game's own editor knew the real counts.
Anything generated from outside should not.

---

## 12. A minimal complete level

Twelve cells: a floor, a platform, one orb, the player, and the door.

```xml
<level>
  <infos><version>0.1.0</version></infos>
  <tc><id/><title/></tc>
  <game>
    <bg><id>BG_city_0</id></bg>
    <goal><id>2</id></goal>
    <character><id>1</id></character>
    <map>
      <cell id="c1" i="0" j="13"><class>W_ville_0100</class><depth>20006</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c2" i="1" j="13"><class>W_ville_0101</class><depth>20005</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c3" i="2" j="13"><class>W_ville_0101</class><depth>20004</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c4" i="3" j="13"><class>W_ville_0001</class><depth>20003</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c5" i="6" j="10"><class>PF_0100</class><depth>40000</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c6" i="7" j="10"><class>PF_0001</class><depth>40000</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c7" i="6" j="9"><class>Item_city</class><depth>80000</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c8" i="1" j="12"><class>Ben10Swampfire</class><depth>110000</depth><dx>15</dx><dy>15</dy></cell>
      <cell id="c9" i="10" j="12"><class>Goal_Items</class><depth>60000</depth>
        <rect><imin>-2</imin><imax>2</imax><jmin>-4</jmin><jmax>1</jmax></rect>
        <dx>15</dx><dy>15</dy></cell>
    </map>
  </game>
</level>
```

Save as `save/swampfire_easy.xml` and it plays.

---

## 13. Checklist before shipping a level

* Exactly one `Ben10*` cell, and its class matches `<character><id>`
* Exactly one `Goal_*` cell, and its class matches `<goal><id>`
* Goal type `2`/`4` → at least one `Item_*`; type `3`/`4` → at least one `Robot_*`
* No two non-wall cells share the same `i`,`j`
* No orb, robot or box sits inside a wall or platform cell
* No `<data>` element anywhere
* Every `class` appears in `tools/class-inventory.json` for the target game

`tools/validate.py` checks all of these. It cannot check whether the level is actually
*beatable* — that still needs a human, because alien abilities change traversal in ways a
static grid analysis does not capture.
