import pygame
from config import *


class GridEditor:
    def __init__(self, floor_manager, store_manager):
        self.floor_manager = floor_manager
        self.store_manager = store_manager
        self.current_tile = PATH
        self.dragging = False
        self.start_pos = None
        self.end_pos = None
        self.error_message = None
        self.error_timer = 0

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def handle_event(self, event):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # Start drag (Shift + LMB)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.dragging = True
                self.start_pos = pygame.mouse.get_pos()
            else:
                self.paint()

        # Update drag preview or freehand paint
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.end_pos = pygame.mouse.get_pos()
            elif mouse_pressed[0]:
                self.paint()

        # Release drag → fill rectangle
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.end_pos = pygame.mouse.get_pos()
                self.fill_rect()
                self.dragging = False
                self.start_pos = None
                self.end_pos = None

        # Tile selection keys
        if event.type == pygame.KEYDOWN:
            tile_keys = {
                pygame.K_0: EMPTY,
                pygame.K_1: PATH,
                pygame.K_2: STORE,
                pygame.K_3: ESCALATOR_UP,
                pygame.K_4: ESCALATOR_DOWN,
                pygame.K_5: MALL_ENTRANCE,
                pygame.K_6: MALL_EXIT,
            }
            if event.key in tile_keys:
                self.current_tile = tile_keys[event.key]

    # ------------------------------------------------------------------
    # Tile placement
    # ------------------------------------------------------------------
    def _place_tile(self, grid, row, col):
        """Place the current tile at (row, col), overwriting whatever is there."""
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return

        tile = self.current_tile

        # Nothing to do if tile is the same
        if grid[row][col] == tile:
            return

        # Clean up paired escalator on adjacent floor before overwriting
        existing = grid[row][col]
        if existing == ESCALATOR_UP:
            self._clear_paired_escalator(row, col, ESCALATOR_UP)
        elif existing == ESCALATOR_DOWN:
            self._clear_paired_escalator(row, col, ESCALATOR_DOWN)

        # Place new tile
        if tile in (ESCALATOR_UP, ESCALATOR_DOWN):
            if self._validate_and_pair_escalator(row, col, tile):
                grid[row][col] = tile
        else:
            grid[row][col] = tile

    def _validate_and_pair_escalator(self, row, col, tile_type):
        """Check adjacent floor exists, stamp the paired escalator there. Returns success."""
        current_floor = self.floor_manager.current_floor
        floors = self.floor_manager.floors

        if tile_type == ESCALATOR_UP:
            if current_floor >= len(floors) - 1:
                self.error_message = "ERROR: No floor above for ESCALATOR_UP"
                self.error_timer = 120
                return False
            target_floor = floors[current_floor + 1]
            paired_tile = ESCALATOR_DOWN
        else:  # ESCALATOR_DOWN
            if current_floor <= 0:
                self.error_message = "ERROR: No floor below for ESCALATOR_DOWN"
                self.error_timer = 120
                return False
            target_floor = floors[current_floor - 1]
            paired_tile = ESCALATOR_UP

        if 0 <= row < len(target_floor) and 0 <= col < len(target_floor[0]):
            target_floor[row][col] = paired_tile

        return True

    def _clear_paired_escalator(self, row, col, tile_type):
        """Remove the paired escalator tile from the adjacent floor."""
        current_floor = self.floor_manager.current_floor
        floors = self.floor_manager.floors

        if tile_type == ESCALATOR_UP and current_floor < len(floors) - 1:
            target_floor = floors[current_floor + 1]
            if 0 <= row < len(target_floor) and 0 <= col < len(target_floor[0]):
                if target_floor[row][col] == ESCALATOR_DOWN:
                    target_floor[row][col] = EMPTY

        elif tile_type == ESCALATOR_DOWN and current_floor > 0:
            target_floor = floors[current_floor - 1]
            if 0 <= row < len(target_floor) and 0 <= col < len(target_floor[0]):
                if target_floor[row][col] == ESCALATOR_UP:
                    target_floor[row][col] = EMPTY

    # ------------------------------------------------------------------
    # Paint / fill  (rescan stores after every edit)
    # ------------------------------------------------------------------
    def paint(self):
        mx, my = pygame.mouse.get_pos()
        grid = self.floor_manager.get_current()
        self._place_tile(grid, my // GRID_SIZE, mx // GRID_SIZE)
        self.store_manager.rescan()

    def fill_rect(self):
        """Fill the dragged rectangle, overwriting all tiles, then rescan."""
        grid = self.floor_manager.get_current()
        x1, y1 = self.start_pos[0] // GRID_SIZE, self.start_pos[1] // GRID_SIZE
        x2, y2 = self.end_pos[0]   // GRID_SIZE, self.end_pos[1]   // GRID_SIZE

        for row in range(min(y1, y2), max(y1, y2) + 1):
            for col in range(min(x1, x2), max(x1, x2) + 1):
                self._place_tile(grid, row, col)

        self.store_manager.rescan()

    # ------------------------------------------------------------------
    # Entrance / exit query helpers (used by BoidManager)
    # ------------------------------------------------------------------
    def get_tile_positions(self, tile_type):
        """Return pixel-center (x, y) positions for all tiles of tile_type on the current floor."""
        grid = self.floor_manager.get_current()
        positions = []
        for row, tiles in enumerate(grid):
            for col, tile in enumerate(tiles):
                if tile == tile_type:
                    positions.append((
                        col * GRID_SIZE + GRID_SIZE // 2,
                        row * GRID_SIZE + GRID_SIZE // 2,
                    ))
        return positions

    def has_entrances(self):
        return bool(self.get_tile_positions(MALL_ENTRANCE))

    def has_exits(self):
        return bool(self.get_tile_positions(MALL_EXIT))

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, screen, show_grid=True):
        grid = self.floor_manager.get_current()

        # EMPTY = 30,30,30
        GRID_LINE_COLOR = (50, 50, 50)

        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                rect  = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                color = TILES_COLORS.get(tile, (80, 80, 80))
                pygame.draw.rect(screen, color, rect)
                if show_grid:
                    pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

        # Drag-rectangle preview
        if self.dragging and self.start_pos and self.end_pos:
            rect = pygame.Rect(
                self.start_pos,
                (self.end_pos[0] - self.start_pos[0],
                 self.end_pos[1] - self.start_pos[1])
            )
            rect.normalize()
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)