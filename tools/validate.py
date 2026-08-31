#!/usr/bin/env python3
"""Validate a gmaker level XML file.

    python tools/validate.py levels/omniverse/swampfire_hard.xml --game omniverse
    python tools/validate.py levels/**/*.xml --game omniverse --quiet

Checks that a level is well-formed and will load. It does NOT check that the level is
beatable - see the README for why that is not something a static check can decide.
"""
import argparse
import collections
import json
import os
import sys
import xml.etree.ElementTree as ET

W, H = 20, 14
HERE = os.path.dirname(os.path.abspath(__file__))

GOAL_NEEDS = {"1": (False, False), "2": (True, False),
              "3": (False, True), "4": (True, True)}   # (items, enemies)
GOAL_CLASS = {"1": "Goal_Neutral", "2": "Goal_Items",
              "3": "Goal_Enemies", "4": "Goal_EnemiesItems"}
PLAYER_CLASS = {
    "1": "Ben10Swampfire", "2": "Ben10Humongousaur", "3": "Ben10Jetray",
    "4": "Ben10Spidermonkey", "5": "Ben10Brainstorm", "6": "Ben10Waterhazard",
    "7": "Ben10Terraspin", "8": "Ben10Cannonbolt", "9": "Ben10Echoecho",
    "10": "Ben10Bigchill", "11": "Ben10Feedback", "12": "Ben10Gravattack",
    "13": "Ben10BallWeevil", "14": "Ben10Bloxx",
    "17": "Ben10Blitzwolfer", "18": "Ben10SnareOh",
}
SOLID_PREFIX = ("W_", "PF")


def inventory(game):
    with open(os.path.join(HERE, "class-inventory.json"), encoding="utf-8") as f:
        inv = json.load(f)
    if game not in inv:
        sys.exit(f"unknown game '{game}' - expected one of {', '.join(inv)}")
    return {c for group in inv[game].values() for c in group}


def check(path, known):
    errors, warnings = [], []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"XML will not parse: {e}"], []

    bg = (root.findtext("game/bg/id") or "").strip()
    gid = (root.findtext("game/goal/id") or "").strip()
    cid = (root.findtext("game/character/id") or "").strip()

    if bg not in known:
        errors.append(f"background '{bg}' is not in this game's library")
    if gid not in GOAL_NEEDS:
        errors.append(f"<goal><id> must be 1-4, got '{gid}'")
    if cid not in PLAYER_CLASS:
        errors.append(f"<character><id> '{cid}' is not a known alien")

    occupied = collections.defaultdict(list)   # (i,j) -> [class] for non-solid
    solid = set()
    counts = collections.Counter()
    player_pos = goal_pos = None

    for cell in root.iter("cell"):
        cls = (cell.findtext("class") or "").strip()
        try:
            i, j = int(cell.get("i")), int(cell.get("j"))
        except (TypeError, ValueError):
            errors.append(f"cell '{cls}' has a bad i/j")
            continue

        if not (0 <= i < W and 0 <= j < H):
            errors.append(f"{cls} at ({i},{j}) is outside the {W}x{H} grid")
        if cls not in known:
            errors.append(f"class '{cls}' at ({i},{j}) is not in this game's library")
        if cell.find("data") is not None:
            errors.append(f"{cls} at ({i},{j}) writes <data> - never write a variant")

        if cls.startswith(SOLID_PREFIX):
            solid.add((i, j))
            continue
        occupied[(i, j)].append(cls)

        if cls.startswith("Ben10"):
            counts["player"] += 1
            player_pos = (i, j)
        elif cls.startswith("Goal_"):
            counts["goal"] += 1
            goal_pos = (i, j)
            if gid in GOAL_CLASS and cls != GOAL_CLASS[gid]:
                errors.append(f"<goal><id>{gid} expects {GOAL_CLASS[gid]}, found {cls}")
        elif cls.startswith("Item_"):
            counts["item"] += 1
        elif cls.startswith("Robot_"):
            counts["robot"] += 1

    if counts["player"] != 1:
        errors.append(f"need exactly one player cell, found {counts['player']}")
    elif cid in PLAYER_CLASS:
        want = PLAYER_CLASS[cid]
        got = next(c for cs in occupied.values() for c in cs if c.startswith("Ben10"))
        if got != want:
            errors.append(f"<character><id>{cid} is {want}, but the placed cell is {got}")
    if counts["goal"] != 1:
        errors.append(f"need exactly one goal cell, found {counts['goal']}")

    if gid in GOAL_NEEDS:
        need_items, need_enemies = GOAL_NEEDS[gid]
        if need_items and not counts["item"]:
            errors.append(f"objective {gid} requires orbs, but there are none")
        if need_enemies and not counts["robot"]:
            errors.append(f"objective {gid} requires enemies, but there are none")

    for pos, classes in occupied.items():
        if len(classes) > 1:
            errors.append(f"{len(classes)} objects share cell {pos}: {', '.join(classes)}")
        if pos in solid:
            errors.append(f"{classes[0]} at {pos} sits inside a wall or platform")

    if player_pos:
        for pos, classes in occupied.items():
            if any(c.startswith("Robot_") for c in classes):
                if abs(pos[0] - player_pos[0]) + abs(pos[1] - player_pos[1]) <= 3:
                    errors.append(f"enemy at {pos} is on top of the spawn {player_pos}")
        if (player_pos[0], player_pos[1] + 1) not in solid:
            warnings.append("nothing under the player - the level starts mid-fall")
    if goal_pos and (goal_pos[0], goal_pos[1] + 1) not in solid:
        warnings.append("nothing under the goal - make sure it can be reached")

    for pos, classes in occupied.items():
        if any(c.startswith(("Robot_", "Object_")) for c in classes):
            if (pos[0], pos[1] + 1) not in solid:
                warnings.append(f"{classes[0]} at {pos} is floating")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--game", default="omniverse",
                    help="omniverse | galactic-monsters (default: omniverse)")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    known = inventory(args.game)
    bad = 0
    for path in args.files:
        errors, warnings = check(path, known)
        name = os.path.basename(path)
        if errors:
            bad += 1
            print(f"FAIL  {name}")
            for e in errors:
                print(f"        error: {e}")
            for w in warnings:
                print(f"        warn:  {w}")
        elif warnings and not args.quiet:
            print(f"ok    {name}")
            for w in warnings:
                print(f"        warn:  {w}")
        elif not args.quiet:
            print(f"ok    {name}")

    total = len(args.files)
    print(f"\n{total - bad}/{total} valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
