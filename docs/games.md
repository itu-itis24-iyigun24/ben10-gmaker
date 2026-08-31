# The games

Two games are known to use this level format. Both were built by Yamago for Cartoon
Network and published as Flash games around 2012–2014.

---

## Ben 10 Omniverse Collection

| | |
|---|---|
| Entry SWF | `GameCreatorBen10.swf` |
| Level path | `save/<alienId>_<slot>.xml` |
| Slots | **2** — `easy` and `hard` |
| Aliens | 13 |
| Wall themes | `ville`, `jungle`, `roche`, `lave`, `lave2` |
| Sprite library | `sprites_ben10.swf` + `sprites_enhancement_ben10.swf` |

### Aliens

`config_oc_ben10.xml` lists them; the id comes from `DataMap.mapCharTab`.

| id | alienId | id | alienId |
|---:|---|---:|---|
| 1 | `swampfire` | 9 | `echoecho` |
| 2 | `humongousaur` | 10 | `bigchill` |
| 4 | `spidermonkey` | 11 | `feedback` |
| 5 | `brainstorm` | 12 | `gravattack` |
| 6 | `waterhazard` | 13 | `ballweevil` |
| 7 | `terraspin` | 14 | `bloxx` |
| 8 | `cannonbolt` | | |

Id `3` (`jetray`) exists in the engine's character table and its class ships in the sprite
library, but the collection's alien list does not include it.

### Two difficulties, not three

The difficulty screen `ScreenChoiceLevelInterS` declares exactly two buttons:

```actionscript
public var hard:UIButton;
public var easy:UIButton;
```

There is no `medium`. A `save/<alien>_medium.xml` file is never requested.

### Hard is gated

```actionscript
if (pDatas.state == LevelDatas.UNLOCK) this.hard.askDisable();
```

`hard` stays disabled until that alien's `easy` level has been completed. Progress is kept
in a Flash `SharedObject`, so it survives between sessions and is not stored in any file
that ships with the game.

Practical consequence when testing: a brand-new hard level cannot be opened until you beat
the easy one for the same alien.

### A full set is 26 files

13 aliens × 2 slots. Any alien/slot without a file will fail to load when selected, so a
complete playable set needs all 26.

---

## Ben 10 Omniverse: Galactic Monsters Collection

| | |
|---|---|
| Entry SWF | `GameCreatorBen10.swf` |
| Level path | `save/<alienId>_<slot>.xml` |
| Slots | **5** — `0` through `4`, shown as LEVEL 1–5 |
| Aliens | 2 |
| Wall themes | `ville`, `jungle`, `roche`, `lave2` |
| Sprite library | `sprites_ben10.swf` + `characters/*.swf` |

### Aliens

| id | alienId | Ability |
|---:|---|---|
| 17 | `blitzwolfer` | double jump; sonic howl pushes objects |
| 18 | `snareoh` | crouch under enemy fire |

`config_oc_ben10.xml` here uses a different attribute shape from the Omniverse Collection:

```xml
<alien id="snareoh" lvlIndex="0"/>
<alien id="blitzwolfer" lvlIndex="0"/>
```

The number of slots is a compiled constant:

```actionscript
public static const NB_LEVELS:int = 5;
```

No difficulty gating — all five slots are selectable from the start.

### A full set is 10 files

2 aliens × 5 slots.

---

## Which game is which file

Both games ship a file called `GameCreatorBen10.swf` and both have a `save/` folder, so it
is easy to mix them up. The quickest tells:

* **Galactic Monsters** keeps everything under `content/localflash/iceboxCN/galacticmonsters/`
  and has a `characters/` subfolder with `snareoh.swf` and `blitzwolfer.swf`.
* **Omniverse Collection** has `sprites_enhancement_ben10.swf`, which Galactic Monsters
  does not.

A level file itself is unambiguous: read `<character><id>` and look it up in the tables above.

---

## Preservation status

Worth recording, since it affects anyone trying to follow these notes:

* **Ben 10 Omniverse: Galactic Monsters Collection** — preserved and playable in Flashpoint
  Archive as a GameZip. Complete.
* **Ben 10 Omniverse Collection** — the game files exist and can be cached from the original
  CDN by playing it, but some regional Flashpoint entries point at dead
  `cartoonnetwork.com.au` / `.es` web wrappers that need a live backend and will not load.
* **Ben 10 Ultimate Alien: The Ultimate Collection** — **incompletely preserved.**
  Flashpoint's own download server returns 404 for its GameData. Flash Museum has only the
  ~64 KB entry loader; the sibling files it requests (`preload.swf` and the rest) return 403.
  A complete file tree does exist on at least one game portal, so the game is recoverable —
  it just is not in the archives yet.

That last one is a concrete, fixable gap if you curate for Flashpoint.
