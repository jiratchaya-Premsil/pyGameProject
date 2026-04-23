import pygame
from config import *

class GridEditior:
    def __init__(self,floor_manager):
        self.floor_manager = floor_manager
        self.current_tile = WALKABLE
        self.dragging = False
        self.start_pos = None
        self.end_pos = None
        self.error_message = None
        self.error_timer = 0

    def handle_event(self, event):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # ------------------------
        # START DRAG (Shift only)
        # ------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.dragging = True
                self.start_pos = pygame.mouse.get_pos()

        # ------------------------
        # DRAGGING RECTANGLE
        # ------------------------
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.end_pos = pygame.mouse.get_pos()

            # 🎯 NEW: draw while holding mouse (no Shift)
            elif mouse_pressed[0]:  # left mouse held
                self.paint()

        # ------------------------
        # RELEASE = fill rectangle
        # ------------------------
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.end_pos = pygame.mouse.get_pos()
                self.fill_rect()
                self.dragging = False
                self.start_pos = None
                self.end_pos = None

        # ------------------------
        # TILE SWITCHING
        # ------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.current_tile = WALKABLE
            if event.key == pygame.K_2:
                self.current_tile = STORE
            if event.key == pygame.K_3:
                self.current_tile = ESCALATOR_UP
            if event.key == pygame.K_4:
                self.current_tile = ESCALATOR_DOWN
            if event.key == pygame.K_5:
                self.current_tile = DOOR
            if event.key == pygame.K_5:
                self.current_tile = DOOR

    def validate_and_place_escalator(self, row, col, tile_type):
        """Validate escalator placement and place corresponding escalator on adjacent floor if valid."""
        current_floor = self.floor_manager.current_floor
        floors = self.floor_manager.floors

        if tile_type == ESCALATOR_UP:
            # Check if there's a higher floor
            if current_floor >= len(floors) - 1:
                self.error_message = "ERROR: No floor above to place ESCALATOR_UP"
                self.error_timer = 120
                return False
            # Place ESCALATOR_DOWN on the upper floor at the same position
            upper_floor = floors[current_floor + 1]
            if 0 <= row < len(upper_floor) and 0 <= col < len(upper_floor[0]):
                upper_floor[row][col] = ESCALATOR_DOWN
            return True

        elif tile_type == ESCALATOR_DOWN:
            # Check if there's a lower floor
            if current_floor <= 0:
                self.error_message = "ERROR: No floor below to place ESCALATOR_DOWN"
                self.error_timer = 120
                return False
            # Place ESCALATOR_UP on the lower floor at the same position
            lower_floor = floors[current_floor - 1]
            if 0 <= row < len(lower_floor) and 0 <= col < len(lower_floor[0]):
                lower_floor[row][col] = ESCALATOR_UP
            return True

        return True

    def fill_rect(self):
        grid = self.floor_manager.get_current()

        x1, y1 = self.start_pos
        x2, y2 = self.end_pos

        x1 //= GRID_SIZE
        y1 //= GRID_SIZE
        x2 //= GRID_SIZE
        y2 //= GRID_SIZE

        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    # Only modify EMPTY tiles when using fill_rect
                    if grid[y][x] == EMPTY:
                        if self.current_tile == ESCALATOR_UP or self.current_tile == ESCALATOR_DOWN:
                            if self.validate_and_place_escalator(y, x, self.current_tile):
                                grid[y][x] = self.current_tile
                        else:
                            grid[y][x] = self.current_tile

    def remove_escalators_from_adjacent_floors(self, row, col):
        """Remove escalators from adjacent floors at the same position."""
        current_floor = self.floor_manager.current_floor
        floors = self.floor_manager.floors

        # Check and remove ESCALATOR_DOWN on floor above
        if current_floor < len(floors) - 1:
            upper_floor = floors[current_floor + 1]
            if 0 <= row < len(upper_floor) and 0 <= col < len(upper_floor[0]):
                if upper_floor[row][col] == ESCALATOR_DOWN:
                    upper_floor[row][col] = WALKABLE

        # Check and remove ESCALATOR_UP on floor below
        if current_floor > 0:
            lower_floor = floors[current_floor - 1]
            if 0 <= row < len(lower_floor) and 0 <= col < len(lower_floor[0]):
                if lower_floor[row][col] == ESCALATOR_UP:
                    lower_floor[row][col] = WALKABLE

    def paint(self):
        mx, my = pygame.mouse.get_pos()
        grid = self.floor_manager.get_current()
        col = mx // GRID_SIZE
        row = my // GRID_SIZE
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            if self.current_tile == ESCALATOR_UP or self.current_tile == ESCALATOR_DOWN:
                if self.validate_and_place_escalator(row, col, self.current_tile):
                    grid[row][col] = self.current_tile
            else:
                # Remove related escalators from adjacent floors before placing tile
                self.remove_escalators_from_adjacent_floors(row, col)
                grid[row][col] = self.current_tile

    def draw(self,screen):
        grid = self.floor_manager.get_current()
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

                color = (50, 50, 50)
                if tile == WALKABLE:
                    color = (200, 200, 200)
                elif tile == STORE:
                    color = (0, 150, 255)
                elif tile == ESCALATOR_UP:
                    color = (255, 200, 0)
                elif tile == ESCALATOR_DOWN:
                    color = (255, 100, 0)
                elif tile == DOOR:
                    color = (0, 255, 0)
                elif tile == DOOR:
                    color = (0, 255, 0)

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (30,30,30), rect, 1)
        # preview rectangle
        if self.dragging and self.start_pos and self.end_pos:
            rect = pygame.Rect(
                self.start_pos,
                (self.end_pos[0] - self.start_pos[0],
                self.end_pos[1] - self.start_pos[1])
            )
            rect.normalize()

            pygame.draw.rect(screen, (255,255,255), rect, 2)
