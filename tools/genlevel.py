"""Generate levels for the Ben 10 gmaker engine.

Grid is 20x14: i is the column (0-19), j is the row (0-13, top to bottom).
Wall, platform and hazard classes are autotiled from their neighbours.
No <data><variant> is ever written - see docs/level-format.md section 11.

    from genlevel import Level

    L = Level(bg="BG_city_1", goal_id=2, char_id=1, wall_theme="ville")
    L.wall_rect(0, 19, 12, 13)
    L.platform(6, 10); L.platform(7, 10)
    L.item(6, 9)
    L.player(1, 11); L.goal(18, 11)
    open("swampfire_easy.xml", "w", encoding="utf-8").write(L.xml())
"""

W, H = 20, 14

WALL_THEMES = ("ville", "jungle", "roche", "lave", "lave2")
HAZARD_KINDS = ("saw", "volt")
ITEM_KINDS = ("city", "jungle", "lava", "phantom")

GOAL_CLASS = {1: "Goal_Neutral", 2: "Goal_Items",
              3: "Goal_Enemies", 4: "Goal_EnemiesItems"}

# DataMap.mapCharTab, 1-based, plus the two Galactic Monsters aliens
PLAYER_CLASS = {
    1: "Ben10Swampfire",   2: "Ben10Humongousaur", 3: "Ben10Jetray",
    4: "Ben10Spidermonkey", 5: "Ben10Brainstorm",  6: "Ben10Waterhazard",
    7: "Ben10Terraspin",   8: "Ben10Cannonbolt",   9: "Ben10Echoecho",
    10: "Ben10Bigchill",  11: "Ben10Feedback",    12: "Ben10Gravattack",
    13: "Ben10BallWeevil", 14: "Ben10Bloxx",
    17: "Ben10Blitzwolfer", 18: "Ben10SnareOh",
}

DEPTH = {"platform": 40000, "fallplat": 50000, "goal": 60000, "generator": 70000,
         "item": 80000, "object": 90000, "robot": 100000, "player": 110000}

RECT_3X3 = (-1, 1, -1, 1)
RECT_GOAL = (-2, 2, -4, 1)


class Level:
    def __init__(self, bg, goal_id, char_id, wall_theme="ville"):
        if goal_id not in GOAL_CLASS:
            raise ValueError(f"goal_id must be 1-4, got {goal_id}")
        if char_id not in PLAYER_CLASS:
            raise ValueError(f"unknown char_id {char_id}")
        if wall_theme not in WALL_THEMES:
            raise ValueError(f"wall_theme must be one of {WALL_THEMES}")
        self.bg, self.goal_id, self.char_id = bg, goal_id, char_id
        self.theme = wall_theme
        self.walls = set()          # (i, j)
        self.plats = set()          # (i, j)
        self.hazards = {}           # (i, j) -> "saw" | "volt"
        self.cells = []             # (i, j, class, depth, rect)
        self._n = 1000

    # ---- terrain -------------------------------------------------------
    def wall(self, i, j):
        self.walls.add((i, j))

    def wall_rect(self, i0, i1, j0, j1):
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                self.walls.add((i, j))

    def platform(self, i, j):
        self.plats.add((i, j))

    def platform_row(self, i0, i1, j):
        for i in range(i0, i1 + 1):
            self.plats.add((i, j))

    def fallplat(self, i, j):
        self._add(i, j, "PFall", DEPTH["fallplat"])

    def hazard(self, i, j, kind="saw"):
        if kind not in HAZARD_KINDS:
            raise ValueError(f"hazard kind must be one of {HAZARD_KINDS}")
        self.hazards[(i, j)] = kind

    def hazard_column(self, i, j0, j1, kind="saw"):
        """Vertical hazard run - the only shape the original levels use."""
        for j in range(j0, j1 + 1):
            self.hazard(i, j, kind)

    # ---- contents ------------------------------------------------------
    def item(self, i, j, kind="city"):
        if kind not in ITEM_KINDS:
            raise ValueError(f"item kind must be one of {ITEM_KINDS}")
        self._add(i, j, f"Item_{kind}", DEPTH["item"])

    def robot(self, i, j, moving=False):
        self._add(i, j, "Robot_Move" if moving else "Robot_Fix",
                  DEPTH["robot"], RECT_3X3)

    def box(self, i, j, solid=False):
        self._add(i, j, "Object_solidBox" if solid else "Object_box",
                  DEPTH["object"], RECT_3X3)

    def generator(self, i, j):
        self._add(i, j, "Enemy_Generator", DEPTH["generator"])

    def player(self, i, j):
        self._add(i, j, PLAYER_CLASS[self.char_id], DEPTH["player"])

    def goal(self, i, j):
        self._add(i, j, GOAL_CLASS[self.goal_id], DEPTH["goal"], RECT_GOAL)

    # ---- internals -----------------------------------------------------
    def _add(self, i, j, cls, depth, rect=None):
        self.cells.append((i, j, cls, depth, rect))

    def _id(self):
        self._n += 137
        return f"instance{self._n}"

    def _wall_class(self, i, j):
        b = lambda p: "1" if p in self.walls else "0"
        mask = b((i, j - 1)) + b((i + 1, j)) + b((i, j + 1)) + b((i - 1, j))
        return f"W_{self.theme}_{mask}"          # U R D L

    def _plat_class(self, i, j):
        b = lambda p: "1" if p in self.plats else "0"
        return f"PF_0{b((i + 1, j))}0{b((i - 1, j))}"   # horizontal only

    def _hazard_class(self, i, j):
        kind = self.hazards[(i, j)]
        b = lambda p: "1" if self.hazards.get(p) == kind else "0"
        return f"W_{kind}_{b((i, j - 1))}0{b((i, j + 1))}0"   # vertical only

    def _wall_depth(self, i, j):
        return max(19975, min(20019, 20019 - i - (H - 1 - j)))

    # ---- output --------------------------------------------------------
    def rows(self):
        """All cells as (i, j, class, depth, rect), in draw order."""
        out = []
        for (i, j) in sorted(self.walls, key=lambda p: (p[1], p[0])):
            out.append((i, j, self._wall_class(i, j), self._wall_depth(i, j), None))
        for (i, j) in sorted(self.hazards, key=lambda p: (p[1], p[0])):
            out.append((i, j, self._hazard_class(i, j), 29990 - j, None))
        for (i, j) in sorted(self.plats, key=lambda p: (p[1], p[0])):
            out.append((i, j, self._plat_class(i, j), DEPTH["platform"], None))
        return out + self.cells

    def xml(self):
        body = []
        for (i, j, cls, depth, rect) in self.rows():
            L = [f'      <cell id="{self._id()}" i="{i}" j="{j}">',
                 f"        <class>{cls}</class>",
                 f"        <depth>{depth}</depth>"]
            if rect:
                a, b_, c, d = rect
                L += ["        <rect>",
                      f"          <imin>{a}</imin>", f"          <imax>{b_}</imax>",
                      f"          <jmin>{c}</jmin>", f"          <jmax>{d}</jmax>",
                      "        </rect>"]
            L += ["        <dx>15</dx>", "        <dy>15</dy>", "      </cell>"]
            body.append("\n".join(L))
        return (
            "<level>\n  <infos>\n    <version>0.1.0</version>\n  </infos>\n"
            "  <tc>\n    <id/>\n    <title/>\n  </tc>\n  <game>\n"
            f"    <bg>\n      <id>{self.bg}</id>\n    </bg>\n"
            f"    <goal>\n      <id>{self.goal_id}</id>\n    </goal>\n"
            f"    <character>\n      <id>{self.char_id}</id>\n    </character>\n"
            "    <map>\n" + "\n".join(body) + "\n    </map>\n  </game>\n</level>\n"
        )

    def ascii(self):
        """Quick text preview of the layout."""
        sym = {"PFall": "~", "Item_": "o", "Robot_": "X", "Object_": "B",
               "Enemy_Generator": "G", "Goal_": "H", "Ben10": "P"}
        g = [["." for _ in range(W)] for _ in range(H)]
        for (i, j) in self.walls:   g[j][i] = "#"
        for (i, j) in self.plats:   g[j][i] = "="
        for (i, j) in self.hazards: g[j][i] = "^"
        for (i, j, cls, _d, _r) in self.cells:
            for pre, s in sym.items():
                if cls.startswith(pre):
                    g[j][i] = s
                    break
        head = "   " + "".join(str(i % 10) for i in range(W))
        return "\n".join([head] + [f"{j:2d} " + "".join(r) for j, r in enumerate(g)])
