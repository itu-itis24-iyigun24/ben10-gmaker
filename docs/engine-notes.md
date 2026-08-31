# Engine notes

Notes on the engine behind the Ben 10 collection games, recovered by decompiling the
games' ActionScript 3. Useful if you want to understand *why* the level format looks the
way it does, or if you are documenting these games elsewhere.

The engine is by **Yamago**, a French studio. Its packages are `com.cn.gmaker.*`
(the game maker) on top of `net.yamago.*` (the studio's general framework). Decompiled
source paths in the games still carry the original build machine's directories, e.g.
`E:\dev\cn\ben10\galactic_monsters\cn.ben10.2014galacticmonsters\...`.

---

## Package map

```
com/cn/gmaker/
  lvld/                    level data
    ALvlD, MyLvlD          parses the level XML, builds the voxel grid
    ALvlMgr, MyLvlMgr      level manager; resolves character/goal ids
    ACell, MyCell          one grid cell; instantiates its sprite
    ADispMgr, MyDispMgr    display manager
    DepthMgr               z-ordering
    sprite/clip/           static cells: PF, Wall, Bonus, Trap, Generator, goal/AGoal
    sprite/mobile/         moving: Mobile, Robot, Shoot, Box, Pushable
    sprite/mobile/player/  APlayer, Player, and one class per alien
    theme/BackGround
  player/game/             GMgr, TimeMgr, CheatMgr, WinScreen, LoseScreen
  player/main/             MainPlayer, TitleCardPlayer, Messages, Help
  utils/                   StateMgr, DataMap, KeyListener, DispatchButtonMovieClip
net/yamago/
  gui, templates, effects, lang, loader, shell, text, tools, utils
net/yamago/ultimatecollection/
  shell/GameCreatorBen10Engine   the collection shell: alien choice, slot choice, load
  shell/SavedDatas, LevelDatas   progress, stored in a Flash SharedObject
  gui/                           screens, alien tabs, level buttons
```

---

## Loading chain

`GameCreatorBen10.swf` is the entry point — its `SymbolClass` tag binds character id 0 to
the document class `GameCreatorBen10`. Despite the name it is the **collection shell**, not
just the level editor.

The player SWF never loads a level itself. The shell fetches the XML and hands it over as an
event payload — `MainPlayer.start()`:

```actionscript
var lisStandalone:Boolean = CtrlPlayerEvent(pEvt).mode == "standalone";
var lvl:XML = CtrlPlayerEvent(pEvt).descript_lvl;
level = patchGoalXml(lvl);
lvlMgr = new MyLvlMgr();
lvlMgr.init(level);
```

There is a `"standalone"` mode that skips the title card and starts a level directly. The
shipped shells do not use it.

Sprite classes are resolved from the sprite library's application domain, loaded separately:

```actionscript
spriteLib = YamzLoader.getApplicationDomain("sprites_" + Config["brand"] + ".swf");
```

That is why `Ben10Bigchill` is not in `player_main_ben10.swf` — the alien classes live in
`sprites_ben10.swf` and `sprites_enhancement_ben10.swf` alongside their artwork.

---

## Physics

Base values, from `Player.as` (Omniverse Collection). Individual aliens override some of
these in their own constructors.

```actionscript
ACC_Y       = -1.3      // gravity acceleration
ACC_X       = 0.775     // ground acceleration
ACC_X_AIR   = 0.575     // air acceleration
IMP         = -15       // jump impulse
V_X_MAX     = 5.8       // max ground speed
V_X_MAX_AIR = 8.5       // max air speed
V_Y_MAX     = 10        // terminal velocity
PES         = 1.55      // weight multiplier
FRICT_HIGH  = 1.37
FROT_H      = 0.1       // ground friction
FROT_AIR    = 0.1       // air friction
V_DERAP     = 3.1       // skid threshold
V_FLIP      = 1.9
V_MIN       = 0.5
FALL_PF_STEP  = 2.5
TO_DOOR_SPEED = 5
B_MAX       = 8
M           = 1         // mass
```

As a rough level-design rule of thumb derived from the shipped levels: platforms sit two to
three rows apart vertically and three to four columns apart horizontally. Aliens with a
double jump comfortably exceed that.

---

## Alien abilities

Traversal differs enough between aliens that the same level is not equally solvable for all
of them. This matters when choosing `<character><id>`.

| Alien | Ability | Effect on traversal |
|---|---|---|
| **Big Chill** | glide | Double jump sets `isFlying`; while flying `PES` drops `1.55 → 0.1` and `V_Y_MAX` `10 → 3`. A slow controlled descent — he cannot gain height without landing. |
| **Blitzwolfer** | double jump | Roughly doubles reachable height. Sonic howl pushes objects. |
| **Bloxx** | builds blocks | `ArmBloxx` / `BlockBloxx`, `registerBlock()` — creates his own platforms. Static reachability analysis is meaningless for Bloxx levels. |
| **Cannonbolt** | rush | `isRushing()`; breaks `Trap` and passes obstacles others cannot. |
| **Jetray** | rush | `isRushing()`; also breaks `BoxSolid`. |
| **Terraspin** | glide | `setModeFly()`, `PES = 2` at rest — heavier, but has a flight mode. |
| **Snare-oh** | crouch | Ducks under enemy fire. No vertical advantage. |
| **Swampfire** | — | No special movement at all. The most constrained alien; a level built for Swampfire is the strictest test of a layout. |

Related: `Trap.as` checks `param1 is Ben10Cannonbolt && Ben10Cannonbolt(param1).isRushing()`,
and `BoxSolid.as` checks the same for `Ben10Jetray`. Some obstacles are deliberately
alien-specific.

---

## The state system

Every cell sprite is a container whose **child sprites are its visual states**.
`StateMgr.parse()` walks the children:

```actionscript
_loc4_ = Object(_loc1_).constructor;
if (_loc1_ is Sprite && _loc4_ != MovieClip) {
   _loc2_ = new State(Sprite(_loc1_), statesByD.length);
   statesByD.push(_loc2_);
   ...
}
```

State counts vary per sprite and between the two games. This is the mechanism behind the
`variant` rule in [level-format.md §11](level-format.md#11-the-variant-rule): passing `-1`
makes the engine pick a valid state at random; passing an out-of-range index crashes.

A sprite with *zero* states is harmless — `setState()` guards with
`if (statesByD.length > 0)` and returns quietly. The crash only happens when states exist
and the index misses.

---

## Unused and leftover content

Things present in the shipped files that the games never show:

**A test shell for the level editor.** `launcher_ben10.swf` contains
`com.cn.gmaker.ShellDummy`, a development harness that loads nine level templates
(`templates/template1..9.xml`), a saved level (`save/saved_level_example.xml`) and
`builder_preload_ben10.swf`, then hands them to the builder:

```actionscript
this.loader.dispatchEvent(new CtrlBuilderEvent(CtrlBuilderEvent.START, this.savedXml, this.templatesTab));
```

None of those template files ship with the games.

**A commented-out alien roster.** `config_oc_ben10.xml` in Galactic Monsters keeps the
Omniverse Collection's full 13-alien list commented out above the two aliens that game
actually uses, with a `state="unavailable" date="MM/DD/YYYY"` scheme for time-gated unlocks
that was clearly used during the original run.

**A disabled online gallery.** `lockbuilder` and `lockGallery` are both `true` in shipped
configs, hiding a "build your own level and publish it" flow. The dead endpoints are still
in the file: `ben10-gamecreator.cartoonnetwork.co.uk`, and `urlGalleryXml`.

**A third difficulty that never existed.** The Omniverse Collection's difficulty screen
(`ScreenChoiceLevelInterS`) declares only two buttons, `easy` and `hard`. There is no
`medium`, even though the file naming scheme would happily accept one.

**Difficulty gating.** Hard is disabled until easy is completed:

```actionscript
if (pDatas.state == LevelDatas.UNLOCK) this.hard.askDisable();
```

Progress lives in a Flash `SharedObject` (`SavedDatas` / `UCLocalUser`), not in any file
that ships with the game.
