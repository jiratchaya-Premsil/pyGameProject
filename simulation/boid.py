import pygame
import random
import math
from config import *

# Walkable tiles a boid is allowed to stand on
WALKABLE = {PATH, MALL_ENTRANCE, MALL_EXIT, ESCALATOR_UP, ESCALATOR_DOWN}

# How close (pixels) a boid must be to a tile centre to "activate" it
TILE_REACH = GRID_SIZE * 0.7


def _tile_centre(col, row):
    return pygame.Vector2(col * GRID_SIZE + GRID_SIZE / 2,
                          row * GRID_SIZE + GRID_SIZE / 2)


class Boid:
    """
    A single mall visitor.

    States
    ------
    wandering   – roams walkable tiles on the current floor
    escalating  – moving toward an escalator tile to change floor
    exiting     – heading toward a MALL_EXIT (floor 0) or MALL_ENTRANCE to despawn
    done        – flagged for removal
    """

    def __init__(self, x, y, floor_index, has_exit):
        self.pos       = pygame.Vector2(x, y)
        self.vel       = pygame.Vector2(random.uniform(-1, 1),
                                        random.uniform(-1, 1)).normalize() * BOID_MIN_SPEED
        self.acc       = pygame.Vector2(0, 0)
        self.max_speed = random.uniform(BOID_MIN_SPEED, BOID_MAX_SPEED)
        self.max_force = BOID_MAX_FORCE
        self.size      = BOID_SIZE

        self.floor              = floor_index
        self.has_exit           = has_exit
        self.escalator_cooldown = 0

        # Wander state
        self.wander_angle  = random.uniform(0, math.tau)
        self.wander_timer  = 0
        self.wander_change = random.randint(*BOID_WANDER_INTERVAL_RANGE)

        # State machine
        self.state        = "wandering"
        self.target       = None   # pixel-space Vector2 for escalating / exiting
        self.target_floor = None   # destination floor when escalating
        self.done         = False

        # Lifespan (randomised per boid)
        self.lifetime = random.randint(*BOID_LIFESPAN_RANGE)
        self.age      = 0

    # ------------------------------------------------------------------ #
    #  Main update                                                         #
    # ------------------------------------------------------------------ #
    def update(self, floors, has_exit):
        if self.done:
            return False

        if self.escalator_cooldown > 0:
            self.escalator_cooldown -= 1

        self.has_exit = has_exit
        self.age += 1
        self.acc = pygame.Vector2(0, 0)

        grid = floors[self.floor]

        if self.state == "wandering":
            if self.age >= self.lifetime:
                self._begin_exit(floors)
            else:
                self._wander(grid)
                self._avoid_walls(grid)

        elif self.state == "escalating":
            self._seek(self.target)
            if self.pos.distance_to(self.target) < TILE_REACH:
                self.floor        = self.target_floor
                self.pos          = pygame.Vector2(self.target)
                self.state        = "wandering"
                self.target       = None
                self.target_floor = None
                self.escalator_cooldown = BOID_ESCALATOR_COOLDOWN

        elif self.state == "exiting":
            self._seek(self.target, BOID_EXIT_SEEK_WEIGHT)
            self._wander(grid)
            self._avoid_walls(grid)
            if self.pos.distance_to(self.target) < TILE_REACH:
                self.done = True
                return False

        # Integrate velocity
        self.vel += self.acc
        spd = self.vel.length()
        if spd > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        elif spd < BOID_MIN_SPEED:
            self.vel.scale_to_length(BOID_MIN_SPEED)

        self.pos += self.vel

        # Clamp to screen bounds
        self.pos.x = max(0, min(self.pos.x, WIDTH  - 1))
        self.pos.y = max(0, min(self.pos.y, HEIGHT - 1))

        # Hard wall constraint: roll back and slide if landed on a wall
        grid = floors[self.floor]
        if not self._is_walkable(grid, self.pos):
            self.pos -= self.vel
            test_x = self.pos + pygame.Vector2(self.vel.x, 0)
            test_y = self.pos + pygame.Vector2(0, self.vel.y)
            moved  = False
            if self._is_walkable(grid, test_x):
                self.pos   = test_x
                self.vel.y *= -0.5
                moved = True
            if self._is_walkable(grid, test_y):
                self.pos   = test_y
                self.vel.x *= -0.5
                moved = True
            if not moved:
                self.vel *= -0.5

        # Escalator check only while wandering
        if self.state == "wandering":
            self._check_escalator(floors)

        return True

    # ------------------------------------------------------------------ #
    #  Drawing                                                             #
    # ------------------------------------------------------------------ #
    def draw(self, screen):
        if self.vel.length() == 0:
            return

        tip   = self.pos + self.vel.normalize() * self.size
        perp  = pygame.Vector2(-self.vel.y, self.vel.x).normalize() * (self.size * 0.5)
        left  = self.pos - self.vel.normalize() * (self.size * 0.4) + perp
        right = self.pos - self.vel.normalize() * (self.size * 0.4) - perp

        color = {
            "wandering":  (255, 220,  80),
            "escalating": ( 80, 200, 255),
            "exiting":    (255, 100, 100),
        }.get(self.state, (200, 200, 200))

        pygame.draw.polygon(screen, color, [tip, left, right])

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #
    def apply_force(self, force):
        self.acc += force

    # -- Wander -------------------------------------------------------- #
    def _wander(self, grid):
        self.wander_timer += 1
        if self.wander_timer >= self.wander_change:
            self.wander_timer  = 0
            self.wander_change = random.randint(*BOID_WANDER_INTERVAL_RANGE)
            self.wander_angle += random.uniform(*BOID_WANDER_ANGLE_CHANGE)

        circle_centre = self.pos + self.vel.normalize() * BOID_WANDER_DISTANCE
        target = circle_centre + pygame.Vector2(
            math.cos(self.wander_angle) * BOID_WANDER_RADIUS,
            math.sin(self.wander_angle) * BOID_WANDER_RADIUS,
        )
        self._seek(target, weight=BOID_WANDER_WEIGHT)

    # -- Walkable check ------------------------------------------------ #
    def _is_walkable(self, grid, pos):
        col = int(pos.x // GRID_SIZE)
        row = int(pos.y // GRID_SIZE)
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return False
        return grid[row][col] in WALKABLE

    # -- Wall avoidance ------------------------------------------------ #
    def _avoid_walls(self, grid):
        if self.vel.length() == 0:
            return

        repulsion = pygame.Vector2(0, 0)
        vn = self.vel.normalize()

        for angle_offset in BOID_AVOID_ANGLE_OFFSETS:
            cos_a = math.cos(angle_offset)
            sin_a = math.sin(angle_offset)
            direction = pygame.Vector2(
                vn.x * cos_a - vn.y * sin_a,
                vn.x * sin_a + vn.y * cos_a,
            )
            for dist in BOID_AVOID_RAY_DISTANCES:
                probe = self.pos + direction * dist
                if not self._is_walkable(grid, probe):
                    away = self.pos - probe
                    if away.length() > 0:
                        away.normalize_ip()
                        repulsion += away * (1.0 / dist)
                    break   # stop casting further along this ray

        if repulsion.length() > 0:
            repulsion.scale_to_length(self.max_force * BOID_AVOID_FORCE_MULTIPLIER)
            self.apply_force(repulsion)
            if self.vel.length() < BOID_MIN_SPEED * 1.5:
                # Nudge out when nearly stuck
                escape = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                escape.scale_to_length(self.max_force * BOID_STUCK_NUDGE_MULTIPLIER)
                self.apply_force(escape)

        # Screen-edge push
        margin    = BOID_EDGE_MARGIN
        edge_push = pygame.Vector2(0, 0)
        if self.pos.x < margin:
            edge_push.x += (margin - self.pos.x) / margin
        elif self.pos.x > WIDTH - margin:
            edge_push.x -= (self.pos.x - (WIDTH - margin)) / margin
        if self.pos.y < margin:
            edge_push.y += (margin - self.pos.y) / margin
        elif self.pos.y > HEIGHT - margin:
            edge_push.y -= (self.pos.y - (HEIGHT - margin)) / margin
        if edge_push.length() > 0:
            edge_push.scale_to_length(self.max_force * BOID_AVOID_FORCE_MULTIPLIER)
            self.apply_force(edge_push)

    # -- Seek ---------------------------------------------------------- #
    def _seek(self, target, weight=1.0):
        desired = target - self.pos
        if desired.length() == 0:
            return
        desired.scale_to_length(self.max_speed)
        steer = (desired - self.vel) * weight
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        self.apply_force(steer)

    # -- Escalator detection ------------------------------------------- #
    def _check_escalator(self, floors):
        if self.escalator_cooldown > 0:
            return

        grid = floors[self.floor]
        col  = int(self.pos.x // GRID_SIZE)
        row  = int(self.pos.y // GRID_SIZE)
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return
        tile = grid[row][col]

        if tile == ESCALATOR_UP and self.floor < len(floors) - 1:
            if random.random() < BOID_ESCALATOR_USE_CHANCE:
                self.state        = "escalating"
                self.target       = _tile_centre(col, row)
                self.target_floor = self.floor + 1

        elif tile == ESCALATOR_DOWN and self.floor > 0:
            if random.random() < BOID_ESCALATOR_USE_CHANCE:
                self.state        = "escalating"
                self.target       = _tile_centre(col, row)
                self.target_floor = self.floor - 1

    # -- Begin exit sequence ------------------------------------------- #
    def _begin_exit(self, floors):
        grid = floors[self.floor]

        # Not on ground floor — seek nearest ESCALATOR_DOWN first
        if self.floor > 0:
            dest = self._nearest_tile(grid, ESCALATOR_DOWN)
            if dest:
                self.state        = "escalating"
                self.target       = dest
                self.target_floor = self.floor - 1
                return
            self.done = True   # no way down — edge case, just despawn
            return

        # Ground floor: head to exit or entrance
        dest = self._nearest_tile(grid, MALL_EXIT if self.has_exit else MALL_ENTRANCE)
        if dest:
            self.state  = "exiting"
            self.target = dest
        else:
            self.done = True

    # -- Nearest tile helper ------------------------------------------- #
    def _nearest_tile(self, grid, tile_type):
        best_dist = float('inf')
        best_pos  = None
        for r, row in enumerate(grid):
            for c, t in enumerate(row):
                if t == tile_type:
                    p = _tile_centre(c, r)
                    d = self.pos.distance_to(p)
                    if d < best_dist:
                        best_dist = d
                        best_pos  = p
        return best_pos