# Running a game locally so your levels load

To test a level you need the game running from a **plain folder on disk**, where you can
edit `save/*.xml` and just relaunch. This page covers how to get there and the three
traps that cost the most time.

> This repository does not contain the games. Get them from
> [Flashpoint Archive](https://flashpointarchive.org/), which preserves them.

---

## 1. Get the game files onto disk

The collections are Flash games made of many SWFs plus XML config, not a single file:

```
GameCreatorBen10.swf          ← entry point
shellOC.swf                   ← shell GUI library
player_main_ben10.swf         ← the level player
sprites_ben10.swf             ← art + alien classes
sprites_enhancement_ben10.swf
player_sound_ben10.swf
preload.swf, launcher_ben10.swf, help_ben10.swf …
config.xml, config_oc_ben10.xml, config_player_ben10.xml, sound_ben10.xml
lang/en/…
save/                         ← the level files
```

Two ways to obtain them:

**From Flashpoint.** Play the game once in Flashpoint. Legacy-type entries are proxied and
cached to `Flashpoint\Legacy\htdocs\<host>\<path>\`; GameZip-type entries are a `.zip` under
`Flashpoint\Data\Games\`. Either way you end up with the full tree. Copy it out to a folder
of your own.

**From a site that hosts the game.** Some sites serve the original file tree directly. The
page's own JavaScript usually names the entry SWF, and the sibling files sit next to it.

---

## 2. Run it with the standalone Flash projector

Flashpoint bundles one, so you probably already have it:

```
C:\Flashpoint\FPSoftware\Flash\flashplayer11_9r900_152_win_sa_debug.exe
```

The `_debug` build is worth using — it can write `trace()` output, and the engine traces
useful things like `Launch level swampfire in hard mode.`

```powershell
& "C:\Flashpoint\FPSoftware\Flash\flashplayer11_9r900_152_win_sa_debug.exe" `
  "C:\ben10oc\GameCreatorBen10.swf"
```

To turn on trace logging, create `%USERPROFILE%\mm.cfg`:

```
ErrorReportingEnable=1
TraceOutputFileEnable=1
MaxWarnings=0
```

The log lands in `%APPDATA%\Macromedia\Flash Player\Logs\flashlog.txt` — create that folder
first if it does not exist.

---

## 3. Trap one: the local security sandbox

Running from `file://`, the game will fail immediately with:

```
Error #2044: Unhandled SecurityErrorEvent. text=Error #2140: Security sandbox violation
```

`#2140` means a *local-with-filesystem* SWF and a *local-with-networking* SWF cannot load
each other. The game loads a chain of SWFs, so it trips on this.

Fix: mark the folder trusted. Create a `.cfg` file in Flash's trust directory containing the
folder path:

```powershell
$trust = "$env:APPDATA\Macromedia\Flash Player\#Security\FlashPlayerTrust"
New-Item -ItemType Directory -Force $trust | Out-Null
[System.IO.File]::WriteAllText("$trust\ben10.cfg", "C:\ben10oc",
    (New-Object System.Text.UTF8Encoding($false)))
```

One line, one time. Everything under that folder becomes trusted.

---

## 4. Trap two: non-ASCII paths

Flash Player 11 (2013) does not reliably handle non-ASCII characters in trusted paths. A
folder like `C:\Users\Emirhan İyigün\Downloads\game` will keep failing with `#2140` even
with a correct trust file.

**Put the game somewhere plain: `C:\ben10oc`, `C:\game`.** This is the single most likely
reason a correct-looking trust file "does not work".

---

## 5. Trap three: Flashpoint ignores your edits

If the game is a **GameZip** entry, Flashpoint mounts the `.zip` from `Data\Games\` and
serves files out of it. Editing a level inside that zip does not reliably reach the game —
you can rebuild the zip and watch the game still play the old level.

That is the reason for running standalone from a plain folder. Once you do, a level edit is
just a file save.

If you *do* need to repack a GameZip for some other reason, clone the original's structure
exactly. Flashpoint's mount rejects zips that differ structurally:

| | Original | A naive `zip -r` |
|---|---|---|
| Entries | 42 | 68 |
| Directory entries | **0** | 26 |
| Compression | all deflate | mixed |
| `create_system` | 0 (DOS) | 3 (Unix) |

The naive rebuild fails to mount and the game will not start. Copy every `ZipInfo` field
from the original and substitute only the file bytes you meant to change.

---

## 6. The edit loop

Once the above is set up:

1. Write `save/<alien>_<slot>.xml`
2. Relaunch the projector
3. Pick that alien and slot

In the Omniverse Collection, remember that **hard is locked until easy is beaten** for that
alien — see [games.md](games.md). If you are iterating on a hard level, either beat easy
once or drop your work-in-progress into the easy slot while testing.
