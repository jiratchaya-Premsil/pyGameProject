from collections import deque
from config import *


class StoreManager:
    """
    Scans the current floor and groups contiguous STORE tiles (4-directional)
    into individual stores, each with a unique ID.

    Call rescan() after any tile edit to keep store data up to date.

    Data:
        stores      : dict[store_id -> set of (row, col)]
        tile_to_store: dict[(row, col) -> store_id]
    """

    def __init__(self, floor_manager):
        self.floor_manager = floor_manager
        self.stores: dict[int, set] = {}        # store_id -> {(row,col), ...}
        self.tile_to_store: dict[tuple, int] = {}  # (row,col) -> store_id
        self._next_id = 1

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def rescan(self):
        """Full BFS rescan of the current floor. Call after every tile edit."""
        self.stores.clear()
        self.tile_to_store.clear()

        grid = self.floor_manager.get_current()
        visited = set()

        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == STORE and (row, col) not in visited:
                    store_id = self._next_id
                    self._next_id += 1
                    cells = self._bfs(grid, row, col, visited)
                    self.stores[store_id] = cells
                    for cell in cells:
                        self.tile_to_store[cell] = store_id

    def store_count(self):
        return len(self.stores)

    def get_store_id(self, row, col):
        """Return the store ID at (row, col), or None if not a store tile."""
        return self.tile_to_store.get((row, col))

    def get_store_cells(self, store_id):
        """Return the set of (row, col) cells belonging to store_id."""
        return self.stores.get(store_id, set())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _bfs(self, grid, start_row, start_col, visited):
        """Flood-fill from (start_row, start_col), returns all connected STORE cells."""
        cells = set()
        queue = deque()
        queue.append((start_row, start_col))
        visited.add((start_row, start_col))

        rows = len(grid)
        cols = len(grid[0])

        while queue:
            row, col = queue.popleft()
            cells.add((row, col))

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = row + dr, col + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and (nr, nc) not in visited
                        and grid[nr][nc] == STORE):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

        return cells