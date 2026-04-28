from simulation.boid import Boid
import random
from config import *


class BoidManager:
    def __init__(self, floor_manager):
        self.floor_manager = floor_manager
        self.boids = []
        self.spawn_timer = 0
        self.spawn_rate = 60  # Spawn every 1 second (60 FPS)

    def clear(self):
        """Remove all boids (called when simulation is stopped)."""
        self.boids.clear()
        self.spawn_timer = 0
        print(f"[BoidManager] All boids cleared.")

    def update(self):
        grid = self.floor_manager.get_current()

        # Spawn new boids at MALL_ENTRANCE tiles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            self.spawn_boid_at_entrance(grid)

        # Update existing boids
        self.boids = [b for b in self.boids if b.update(grid)]

    def spawn_boid_at_entrance(self, grid):
        entrance_positions = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == MALL_ENTRANCE:
                    entrance_positions.append(
                        (x * GRID_SIZE + GRID_SIZE / 2,
                         y * GRID_SIZE + GRID_SIZE / 2)
                    )

        if entrance_positions:
            pos = random.choice(entrance_positions)
            print(f"[BoidManager] Spawning boid at {pos}")
            self.boids.append(Boid(pos[0], pos[1]))

    def draw(self, screen):
        for b in self.boids:
            b.draw(screen)