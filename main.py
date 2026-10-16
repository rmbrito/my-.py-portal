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

"""Tkinter window that draws the world as ASCII text. Run: python main.py"""
import tkinter as tk
from tkinter import font as tkfont

from levels import load_levels
from world import World, GREEN, YELLOW, WALL, GLASS, EXIT

BG = "#101010"
COLORS = {WALL: "#7a7a7a", GLASS: "#4dd0e1", EXIT: "#ff4fd8", ".": "#3a3a3a"}
PORTAL_COLOR = {GREEN: "#39ff14", YELLOW: "#ffd800"}
ARROWS = {(0, -1): "^", (0, 1): "v", (-1, 0): "<", (1, 0): ">"}
KEYS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
MENU = ["Resume", "Restart level", "Quit"]
MIN_COLS = 46


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Portal Maker (ASCII)")
        self.font = tkfont.Font(family="Courier", size=18, weight="bold")
        self.cw = self.font.measure("M")
        self.lh = self.font.metrics("linespace")
        self.levels = load_levels()
        self.index = 0
        self.mode = "play"          # play | menu | confirm | won
        self.sel = 0
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.root.bind("<Key>", self.on_key)
        self.load(0)

    # ---- level handling ------------------------------------------------
    def load(self, index):
        self.index = index
        self.world = World(self.levels[index])
        self.cols = max(self.world.w, MIN_COLS)
        self.rows = self.world.h + 4
        self.canvas.config(width=self.cols * self.cw, height=self.rows * self.lh)
        self.mode = "play"
        self.draw()

    # ---- input ---------------------------------------------------------
    def on_key(self, e):
        k = e.keysym.lower()
        w = self.world
        if self.mode == "play":
            if k in KEYS:
                w.move(*KEYS[k])
            elif k == "k":
                w.fire(GREEN)
            elif k == "l":
                w.fire(YELLOW)
            elif k == "j":
                w.toggle_hold()
            elif k == "c":
                w.clear_portals()
            elif k == "r":
                self.mode = "confirm"
            elif k == "escape":
                self.mode, self.sel = "menu", 0
            if w.won:
                self.mode = "won"
        elif self.mode == "menu":
            if k in ("w", "up"):
                self.sel = (self.sel - 1) % len(MENU)
            elif k in ("s", "down"):
                self.sel = (self.sel + 1) % len(MENU)
            elif k == "escape":
                self.mode = "play"
            elif k in ("return", "space"):
                if self.sel == 0:
                    self.mode = "play"
                elif self.sel == 1:
                    self.load(self.index)
                else:
                    self.root.destroy()
                    return
        elif self.mode == "confirm":
            if k == "y":
                self.load(self.index)
            elif k in ("n", "escape"):
                self.mode = "play"
        elif self.mode == "won":
            if k == "r":
                self.mode = "confirm"
            elif k == "escape":
                self.mode, self.sel = "menu", 0
            elif k == "return":
                if self.index + 1 < len(self.levels):
                    self.load(self.index + 1)
                else:
                    self.load(0)
                return
        self.draw()

    # ---- drawing -------------------------------------------------------
    def put(self, cx, cy, ch, color):
        self.canvas.create_text((cx + 0.5) * self.cw, (cy + 0.5) * self.lh,
                                text=ch, fill=color, font=self.font)

    def draw(self):
        c, w = self.canvas, self.world
        c.delete("all")
        ox = (self.cols - w.w) // 2
        fx, fy = w.player[0] + w.facing[0], w.player[1] + w.facing[1]
        for y in range(w.h):
            for x in range(w.w):
                t = w.tile(x, y)
                ch, col = t, COLORS.get(t, "#3a3a3a")
                if t == ".":
                    ch = "\u00b7"
                for color in w.portal_at(x, y):
                    ch, col = "O", PORTAL_COLOR[color]
                if (x, y) in w.boxes:
                    ch, col = "B", ("#ff9f43" if (x, y) == w.held else "#c47a2c")
                if (x, y) == w.player:
                    ch, col = "@", "#ffffff"
                elif (x, y) == (fx, fy) and not w.solid(x, y) and (x, y) not in w.boxes:
                    ch, col = ARROWS[w.facing], "#ff5555"
                self.put(ox + x, y, ch, col)
        base = w.h + 1
        info = "Level %d/%d   Moves: %d   %s" % (
            self.index + 1, len(self.levels), w.moves,
            "Holding box" if w.held else "")
        keys = "WASD move  K green  L yellow  J hold  C clear  R restart  ESC menu"
        self.put_line(base, info, "#dddddd")
        self.put_line(base + 1, keys, "#888888")
        if self.mode == "menu":
            self.overlay(["== MENU =="] + [("> " if i == self.sel else "  ") + m
                                           for i, m in enumerate(MENU)]
                         + ["", "W/S + Enter, ESC to resume"])
        elif self.mode == "confirm":
            self.overlay(["Restart level?", "", "Y = yes    N = no"])
        elif self.mode == "won":
            last = self.index + 1 >= len(self.levels)
            self.overlay(["LEVEL COMPLETE!", "",
                          "Enter = play again from level 1" if last
                          else "Enter = next level"])

    def put_line(self, row, text, color):
        c = self.canvas
        c.create_text(self.cw // 2, (row + 0.5) * self.lh, text=text,
                      fill=color, font=self.font, anchor="w")

    def overlay(self, lines):
        width = max(len(s) for s in lines) + 4
        x0 = (self.cols - width) / 2 * self.cw
        y0 = (self.rows - len(lines) - 2) / 2 * self.lh
        self.canvas.create_rectangle(x0, y0, x0 + width * self.cw,
                                     y0 + (len(lines) + 2) * self.lh,
                                     fill="#000000", outline="#ffffff")
        for i, s in enumerate(lines):
            self.canvas.create_text(self.cols * self.cw / 2, y0 + (i + 1.5) * self.lh,
                                    text=s, fill="#ffffff", font=self.font)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
