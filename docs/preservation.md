# Preservation report

Notes on how well these games survive in public archives, written for anyone curating
them. Every claim below was checked directly; the date and the evidence are given so the
findings can be re-verified or challenged.

**Checked:** 31 August 2026.

---

## Summary

| Game | Status |
|---|---|
| Ben 10 Omniverse: Galactic Monsters Collection | Complete and playable in Flashpoint |
| Ben 10 Omniverse Collection | Playable, but some regional entries are dead |
| Ben 10 Ultimate Alien: The Ultimate Collection | **Incomplete — GameData missing** |

---

## Ben 10 Ultimate Alien: The Ultimate Collection

This is the one worth a curator's time.

**Flashpoint entry:** `1e4adb98-35f5-e6da-fe14-a71e22531565`

**Symptom.** Launching it fails before the game starts. The launcher reports:

```
No working Sources available for this GameData.
Downloading from Source "Flashpoint Project"
  …download.flashpointarchive.org/gib-roms/Games/1e4adb98-35f5-e6da-fe14-a71e22531…
failed: Request failed with status code 404
```

The metadata entry exists; the GameData archive behind it does not.

**Launch command** (from the entry's own metadata):

```
http://tbsila.cdn.turner.com/toonla/images/cnemea/content/14/game/
  ultimate-collection/za/ben10ua-ultimate_collection-en/
  1e4adb98-35f5-e6da-fe14-a71e22531565.swf
```

### Other archives are also incomplete

Flash Museum serves the entry SWF (63.9 KB, `CWS` header, HTTP 200) but nothing else. The
game's first dependency fails:

```
Loading SWF file …/1e4adb98-35f5-e6da-fe14-a71e22531565.swf     OK
ERROR core/src/loader.rs:853  Error during movie loading of
      "…/preload.swf": HttpNotOk("Got ", 403, false, 0)
```

That entry SWF is only a loader — 64 KB with no game content — so having it alone is not
enough to run or to curate.

### A working copy exists

NuMuKi hosts a complete-enough tree at
`files.numuki.com/games/ben-10/ultimate-collection/`. Verified present (HTTP 200, correct
file signatures):

| File | Size |
|---|---|
| `GameCreatorBen10.swf` | 63.9 KB |
| `preload.swf` | 90.6 KB |
| `player_main_ben10.swf` | 163.3 KB |
| `player_preload_ben10.swf` | 42.0 KB |
| `player_sound_ben10.swf` | 1519.3 KB |
| `sprites_ben10.swf` | 2267.8 KB |
| `config.xml` | 0.4 KB |
| `config_player_ben10.xml` | 0.7 KB |
| `sound_ben10.xml` | 4.1 KB |
| `lang/en/main_en.xml` | 5.4 KB |
| `lang/en/logo.png` | 31.5 KB |

Loaded through the site's own player, the game reaches the Cartoon Network splash and its
preloader advances (0% → 7% while observed), so the dependency chain resolves — it is not
stalling on a missing file the way Flash Museum's copy does. Not verified past the loading
screen.

This is a **different build** from the Omniverse Collection, not a relabelled copy:
`config.xml` reports version `0.1.0` (Omniverse: `1.0.3`) and declares only `en`, while
`config_player_ben10.xml` reports `1.1.0` with a thirteen-language list. Its audio bank is
also distinct — ten alien themes, all shorter cuts than the Omniverse versions of the same
tracks, with only `cannonbolt` identical.

The full file list should be captured with Flashpoint's own tooling rather than guessed;
the names above were probed by hand and the tree may hold more.

---

## Ben 10 Omniverse Collection

Playable, and the game files can be obtained by running it — a Legacy-type entry caches
them from the original CDN into `Flashpoint\Legacy\htdocs\`. The CDN at
`tbsila.cdn.turner.com` was still serving them when checked.

Some regional entries do not work. Ones pointing at `gamecreator.cartoonnetwork.com.au` and
the `.es` equivalent are not SWF games but web applications: `tools/xml/config.php` asks for
a `/do.service` backend and a `login.swf` SSO endpoint, both long dead. They hang on the
loading screen and cannot be revived without the server.

---

## Ben 10 Omniverse: Galactic Monsters Collection

Complete. Preserved as a GameZip and plays without issue. Its tree lives under
`content/localflash/iceboxCN/galacticmonsters/` — 21 SWFs, four config XMLs, localisation,
and all ten of its level files.

Useful as a reference: it is the only one of the three whose original level files are all
present, which is what made documenting the level format possible.

---

## A note for curators repacking a GameZip

If you rebuild one of these zips, clone the original's structure exactly. Flashpoint's mount
rejects a naively rebuilt archive and the game will not start:

| | Original | `zip -r` rebuild |
|---|---|---|
| Entries | 42 | 68 |
| Directory entries | 0 | 26 |
| Compression | all deflate | mixed |
| `create_system` | 0 (DOS) | 3 (Unix) |

Copy every `ZipInfo` field from the original and substitute only the bytes you meant to
change.
