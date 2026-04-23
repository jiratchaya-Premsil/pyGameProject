import pygame
import random
import math
from config import *

class Boid:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))
        self.acc = pygame.Vector2(0, 0)
        self.max_speed = 2
        self.max_force = 0.1
        self.size = 8
        self.state = "wandering"  # wandering, exiting
        self.exit_timer = 0

    def update(self, grid):
        # Reset acceleration
        self.acc = pygame.Vector2(0, 0)

        # Apply behaviors based on state
        if self.state == "wandering":
            self.wander()
            self.avoid_obstacles(grid)
            self.check_for_exit(grid)
        elif self.state == "exiting":
            self.seek_exit(grid)
            self.exit_timer += 1
            if self.exit_timer > 300:  # Remove after 5 seconds
                return False  # Signal to remove this boid

        # Update velocity and position
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel

        # Boundary check - wrap around or bounce
        if self.pos.x < 0:
            self.pos.x = 1000
        elif self.pos.x > 1000:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 700
        elif self.pos.y > 700:
            self.pos.y = 0

        return True

    def wander(self):
        # Simple wandering behavior
        wander_force = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))
        wander_force.scale_to_length(0.5)
        self.apply_force(wander_force)

    def avoid_obstacles(self, grid):
        # Check nearby tiles and avoid EMPTY tiles
        check_distance = 20
        ahead = self.pos + self.vel.normalize() * check_distance

        col = int(ahead.x // GRID_SIZE)
        row = int(ahead.y // GRID_SIZE)

        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            if grid[row][col] == EMPTY:
                # Steer away from obstacle
                force = self.pos - ahead
                if force.length() > 0:
                    force.scale_to_length(self.max_force)
                    self.apply_force(force)

    def check_for_exit(self, grid):
        # Check if near a DOOR tile
        col = int(self.pos.x // GRID_SIZE)
        row = int(self.pos.y // GRID_SIZE)

        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            if grid[row][col] == DOOR:
                self.state = "exiting"

    def seek_exit(self, grid):
        # Find nearest DOOR and move towards it
        nearest_door = None
        min_dist = float('inf')

        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == DOOR:
                    door_pos = pygame.Vector2(x * GRID_SIZE + GRID_SIZE/2, y * GRID_SIZE + GRID_SIZE/2)
                    dist = (door_pos - self.pos).length()
                    if dist < min_dist:
                        min_dist = dist
                        nearest_door = door_pos

        if nearest_door:
            desired = nearest_door - self.pos
            if desired.length() > 0:
                desired.scale_to_length(self.max_speed)
                steer = desired - self.vel
                if steer.length() > self.max_force:
                    steer.scale_to_length(self.max_force)
                self.apply_force(steer)

    def apply_force(self, force):
        self.acc += force

    def draw(self, screen):
        # Draw as arrow pointing in velocity direction
        angle = math.atan2(self.vel.y, self.vel.x)

        # Arrow points
        tip = self.pos + self.vel.normalize() * self.size
        left = self.pos + pygame.Vector2(
            self.vel.x * 0.6 - self.vel.y * 0.3,
            self.vel.y * 0.6 + self.vel.x * 0.3
        ).normalize() * (self.size * 0.7)
        right = self.pos + pygame.Vector2(
            self.vel.x * 0.6 + self.vel.y * 0.3,
            self.vel.y * 0.6 - self.vel.x * 0.3
        ).normalize() * (self.size * 0.7)

        # Color based on state
        color = (255, 100, 100) if self.state == "wandering" else (100, 255, 100)

        pygame.draw.polygon(screen, color, [tip, left, self.pos, right])