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

"""Level loading: every maps/*.txt file is one level (sorted by name).

Map legend:  #=wall  .=floor  ==glass (blocks walking, rays pass)
             @=player start  B=box  X=exit
"""
from pathlib import Path

MAP_DIR = Path(__file__).parent / "maps"

FALLBACK = [
    "##########",
    "#@.......#",
    "#..B.....#",
    "#.......X#",
    "##########",
]


def load_levels():
    levels = []
    for path in sorted(MAP_DIR.glob("*.txt")):
        rows = [r.rstrip("\n") for r in path.read_text(encoding="utf-8").splitlines()]
        rows = [r for r in rows if r.strip()]
        if rows:
            levels.append(rows)
    return levels or [FALLBACK]
