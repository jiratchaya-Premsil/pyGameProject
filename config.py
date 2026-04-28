# pygame config
WIDTH = 1000
HEIGHT = 640
FPS = 60

GRID_SIZE = 20

# tile type constants
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

# simulation states
SIM_STOP  = "STOP"
SIM_START = "START"