from collections import deque
from config import *


class StoreManager:
    """
    Scans ALL floors and groups contiguous tiles of the same type
    (4-directional) into individual logical units.

    - STORE tiles   → grouped into stores with unique IDs
    - MALL_ENTRANCE → grouped into entrance zones (count only, no ID)
    - MALL_EXIT     → grouped into exit zones (count only, no ID)

    Call rescan() after any tile edit or floor add/remove to keep data
    up to date.

    Data:
        stores        : dict[store_id -> set of (floor, row, col)]
        tile_to_store : dict[(floor, row, col) -> store_id]
        _entrance_count : int
        _exit_count     : int
    """

    def __init__(self, floor_manager):
        self.floor_manager = floor_manager
        self.stores: dict[int, set] = {}
        self.tile_to_store: dict[tuple, int] = {}
        self._next_id = 1
        self._entrance_count = 0
        self._exit_count = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def rescan(self):
        """Full BFS rescan across ALL floors. Call after every tile edit or floor change."""
        self.stores.clear()
        self.tile_to_store.clear()
        self._entrance_count = 0
        self._exit_count = 0

        floors = self.floor_manager.floors

        visited_store    = set()
        visited_entrance = set()
        visited_exit     = set()

        for floor_idx, grid in enumerate(floors):
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    tile = grid[row][col]
                    key  = (floor_idx, row, col)

                    if tile == STORE and key not in visited_store:
                        store_id = self._next_id
                        self._next_id += 1
                        cells = self._bfs(floors, floor_idx, row, col, STORE, visited_store)
                        self.stores[store_id] = cells
                        for cell in cells:
                            self.tile_to_store[cell] = store_id

                    elif tile == MALL_ENTRANCE and key not in visited_entrance:
                        self._bfs(floors, floor_idx, row, col, MALL_ENTRANCE, visited_entrance)
                        self._entrance_count += 1

                    elif tile == MALL_EXIT and key not in visited_exit:
                        self._bfs(floors, floor_idx, row, col, MALL_EXIT, visited_exit)
                        self._exit_count += 1

    def store_count(self):
        return len(self.stores)

    def entrance_count(self):
        return self._entrance_count

    def exit_count(self):
        return self._exit_count

    def get_store_id(self, floor_idx, row, col):
        """Return the store ID at (floor, row, col), or None if not a store tile."""
        return self.tile_to_store.get((floor_idx, row, col))

    def get_store_cells(self, store_id):
        """Return the set of (floor, row, col) cells belonging to store_id."""
        return self.stores.get(store_id, set())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _bfs(self, floors, start_floor, start_row, start_col, tile_type, visited):
        """
        Flood-fill from (start_floor, start_row, start_col) for tile_type.
        Spreads within the same floor only (stores don't merge across floors).
        Returns all connected cells as a set of (floor, row, col).
        """
        cells = set()
        queue = [(start_floor, start_row, start_col)]
        visited.add((start_floor, start_row, start_col))

        grid = floors[start_floor]
        rows = len(grid)
        cols = len(grid[0])

        while queue:
            f, r, c = queue.pop()
            cells.add((f, r, c))

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                key = (f, nr, nc)
                if (0 <= nr < rows and 0 <= nc < cols
                        and key not in visited
                        and floors[f][nr][nc] == tile_type):
                    visited.add(key)
                    queue.append(key)

        return cells