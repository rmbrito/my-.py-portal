# Portal Maker - ASCII top-down portal game
# Copyright (C) 2026 The Portal Maker authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Game rules and minimal physics (no GUI code here)."""

WALL, FLOOR, GLASS, EXIT = "#", ".", "=", "X"
GREEN, YELLOW = "green", "yellow"
OTHER = {GREEN: YELLOW, YELLOW: GREEN}


class World:
    def __init__(self, rows):
        self.h = len(rows)
        self.w = max(len(r) for r in rows)
        self.grid, self.boxes = [], set()
        self.start = (1, 1)
        for y, row in enumerate(rows):
            line = []
            for x, ch in enumerate(row.ljust(self.w, WALL)):
                if ch == "@":
                    self.start, ch = (x, y), FLOOR
                elif ch == "B":
                    self.boxes.add((x, y))
                    ch = FLOOR
                line.append(ch if ch in (WALL, GLASS, EXIT) else FLOOR)
            self.grid.append(line)
        self.player = self.start
        self.facing = (0, -1)      # aim arrow = last movement direction
        self.portals = {GREEN: None, YELLOW: None}  # color -> (x, y, nx, ny)
        self.held = None           # position of the held box
        self.moves = 0
        self.won = False

    # ---- queries -------------------------------------------------------
    def tile(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return WALL

    def solid(self, x, y):
        return self.tile(x, y) in (WALL, GLASS)

    def free(self, x, y):
        return not self.solid(x, y) and (x, y) not in self.boxes

    def portal_at(self, x, y):
        return [c for c, p in self.portals.items() if p and p[:2] == (x, y)]

    # ---- actions -------------------------------------------------------
    def move(self, dx, dy):
        if self.won:
            return
        self.facing = (dx, dy)
        px, py = self.player
        tx, ty = px + dx, py + dy
        if self.held:
            self._move_holding(dx, dy)
            return
        for color in self.portal_at(tx, ty):          # portal collision
            nx, ny = self.portals[color][2:]
            if (dx, dy) == (-nx, -ny):                # entered from open side
                dest = self.portals[OTHER[color]]
                if dest:
                    ex, ey = dest[0] + dest[2], dest[1] + dest[3]
                    if self.free(ex, ey):
                        self.player, self.facing = (ex, ey), (dest[2], dest[3])
                        self._step_done()
                return
        if self.solid(tx, ty):
            return
        if (tx, ty) in self.boxes:                    # push a box
            bx, by = tx + dx, ty + dy
            if not self.free(bx, by):
                return
            self.boxes.remove((tx, ty))
            self.boxes.add((bx, by))
        self.player = (tx, ty)
        self._step_done()

    def _move_holding(self, dx, dy):
        px, py = self.player
        nx, ny = px + dx, py + dy
        bx, by = nx + dx, ny + dy
        others = self.boxes - {self.held}
        ok = lambda x, y: not self.solid(x, y) and (x, y) not in others
        if ok(nx, ny) and ok(bx, by):
            self.boxes.discard(self.held)
            self.held = (bx, by)
            self.boxes.add(self.held)
            self.player = (nx, ny)
            self._step_done()

    def _step_done(self):
        self.moves += 1
        if self.tile(*self.player) == EXIT:
            self.won = True

    def toggle_hold(self):
        if self.held:
            self.held = None
            return
        front = (self.player[0] + self.facing[0], self.player[1] + self.facing[1])
        if front in self.boxes:
            self.held = front

    def fire(self, color):
        dx, dy = self.facing
        x, y = self.player
        while True:
            x, y = x + dx, y + dy
            if (x, y) in self.boxes:
                return
            t = self.tile(x, y)
            if t == GLASS:
                continue
            if t == WALL:
                break
            if not (0 <= x < self.w and 0 <= y < self.h):
                return
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        new = (x, y, -dx, -dy)
        if self.portals[OTHER[color]] == new:
            return
        self.portals[color] = new

    def clear_portals(self):
        self.portals = {GREEN: None, YELLOW: None}
