# Pygame config
WIDTH  = 1000
HEIGHT = 640
FPS    = 60

GRID_SIZE = 20

# Tile type constants
EMPTY          = 0
PATH           = 1
STORE          = 2
ESCALATOR_UP   = 3
ESCALATOR_DOWN = 4
MALL_ENTRANCE  = 5
MALL_EXIT      = 6

TILES = {
    EMPTY:          "EMPTY",
    PATH:           "PATH",
    STORE:          "STORE",
    ESCALATOR_UP:   "ESCALATOR_UP",
    ESCALATOR_DOWN: "ESCALATOR_DOWN",
    MALL_ENTRANCE:  "MALL_ENTRANCE",
    MALL_EXIT:      "MALL_EXIT",
}

TILES_COLORS = {
    EMPTY:          (30,  30,  30),   # dark background
    PATH:           (200, 200, 200),  # light grey
    STORE:          (255, 100,   0),  # orange
    ESCALATOR_UP:   (0,   255, 255),  # cyan
    ESCALATOR_DOWN: (255,   0, 255),  # magenta
    MALL_ENTRANCE:  (0,   255,   0),  # green
    MALL_EXIT:      (255,   0,   0),  # red
}

# Simulation states
SIM_STOP  = "STOP"
SIM_START = "START"

# ===========================================================================
#  Boid parameters
# ===========================================================================

# --- Spawning / population ------------------------------------------------ #
SPAWN_RATE = 30          # frames between spawn attempts
MAX_BOIDS  = 200         # hard cap on simultaneous boids

# --- Appearance ----------------------------------------------------------- #
BOID_SIZE  = 5           # triangle half-length in pixels

# --- Lifespan ------------------------------------------------------------- #
# Each boid picks a random lifetime from this range (frames).
# At 60 FPS: (1200, 2400) → 20–40 seconds on screen.
BOID_LIFESPAN_RANGE = (1200, 2400)

# --- Velocity ------------------------------------------------------------- #
BOID_MIN_SPEED = 0.2     # pixels/frame — never drops below this
BOID_MAX_SPEED = 2.0     # pixels/frame — each boid samples from [MIN, MAX]
BOID_MAX_FORCE = 0.1     # maximum steering force applied per frame

# --- Wander behaviour ----------------------------------------------------- #
BOID_WANDER_RADIUS        = 25.0          # radius of the wander circle (px)
BOID_WANDER_DISTANCE      = 35.0          # distance ahead to project the circle (px)
BOID_WANDER_ANGLE_CHANGE  = (-0.3, 0.3)  # random delta added to wander angle each tick
BOID_WANDER_INTERVAL_RANGE = (60, 120)   # frames between angle updates
BOID_WANDER_WEIGHT        = 0.4          # force weight for wander steering

# --- Seek behaviour ------------------------------------------------------- #
BOID_SEEK_WEIGHT      = 1.0   # default seek force weight
BOID_EXIT_SEEK_WEIGHT = 0.7   # seek weight when heading to exit (blended with wander)

# --- Wall / obstacle avoidance ------------------------------------------- #
BOID_AVOID_FORCE_MULTIPLIER = 2.0   # scales the wall repulsion force
BOID_STUCK_NUDGE_MULTIPLIER = 2.0   # scales the random escape nudge when nearly stuck
BOID_AVOID_RAY_DISTANCES    = (     # probe distances along each ray (px)
    GRID_SIZE * 0.8,
    GRID_SIZE * 1.5,
    GRID_SIZE * 2.2,
)
BOID_AVOID_ANGLE_OFFSETS = (        # ray angles relative to current heading (radians)
     0.0,
    -0.25,
     0.25,
    -0.6,
     0.6,
)

# --- Edge avoidance ------------------------------------------------------- #
BOID_EDGE_MARGIN = GRID_SIZE * 1.2  # px from screen edge before push-back kicks in

# --- Escalator ------------------------------------------------------------ #
BOID_ESCALATOR_USE_CHANCE = 0.02    # probability per frame of using an escalator tile
BOID_ESCALATOR_COOLDOWN   = 30     # frames before a boid can use another escalator