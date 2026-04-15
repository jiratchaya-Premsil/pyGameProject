import pygame
from config import *

class GridEditior:
    def __init__(self,floor_manager):
        self.floor_manager = floor_manager
        self.current_tile = WALKABLE
        self.dragging = False
        self.start_pos = None
        self.end_pos = None

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
                self.current_tile = ESCALATOR
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
                    grid[y][x] = self.current_tile

    def paint(self):
        mx, my = pygame.mouse.get_pos()
        grid = self.floor_manager.get_current()
        col = mx // GRID_SIZE
        row = my // GRID_SIZE
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
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
                elif tile == ESCALATOR:
                    color = (255, 200, 0)

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
