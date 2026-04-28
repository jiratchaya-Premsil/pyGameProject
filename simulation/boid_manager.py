import random
from config import *
from simulation.boid import Boid


class BoidManager:
    def __init__(self, floor_manager):
        self.floor_manager = floor_manager
        self.boids: list[Boid] = []
        self.spawn_timer = 0
        self.spawn_rate  = SPAWN_RATE

    # ------------------------------------------------------------------ #
    def clear(self):
        """Remove all boids (called when simulation is stopped)."""
        self.boids.clear()
        self.spawn_timer = 0
        print("[BoidManager] All boids cleared.")

    # ------------------------------------------------------------------ #
    def update(self):
        floors   = self.floor_manager.floors
        has_exit = self._any_exit_exists(floors[0])   # exits only on floor 0

        # -- Spawn ---------------------------------------------------- #
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            if len(self.boids) < MAX_BOIDS:
                self._spawn_boid(floors[0], has_exit)

        # -- Individual updates (no separation pass) ------------------ #
        self.boids = [b for b in self.boids
                      if b.update(floors, has_exit)]

    # ------------------------------------------------------------------ #
    def draw(self, screen):
        current = self.floor_manager.current_floor
        for b in self.boids:
            if b.floor == current:
                b.draw(screen)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #
    def _any_exit_exists(self, ground_grid):
        for row in ground_grid:
            for tile in row:
                if tile == MALL_EXIT:
                    return True
        return False

    def _spawn_boid(self, ground_grid, has_exit):
        """Spawn one boid on a random MALL_ENTRANCE tile on floor 0."""
        entrances = []
        for r, row in enumerate(ground_grid):
            for c, tile in enumerate(row):
                if tile == MALL_ENTRANCE:
                    entrances.append((c, r))

        if not entrances:
            return

        c, r = random.choice(entrances)
        x = c * GRID_SIZE + GRID_SIZE / 2
        y = r * GRID_SIZE + GRID_SIZE / 2
        self.boids.append(Boid(x, y, floor_index=0, has_exit=has_exit))