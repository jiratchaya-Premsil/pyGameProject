from config import *

class FloorManager:
    def __init__(self):
        self.floors = [self.create_floor()]
        self.current_floor = 0

    def create_floor(self):
        cols = WIDTH // GRID_SIZE
        rows = HEIGHT // GRID_SIZE
        return [[EMPTY for _ in range(cols)] for _ in range(rows)]

    def add_floor(self):
        """Append a new empty floor at the top."""
        self.floors.append(self.create_floor())

    def remove_top_floor(self):
        """Remove the highest floor. No-op if only one floor exists.
        Also clears any ESCALATOR_UP tiles on the floor below that
        were pointing up into the now-deleted floor.
        """
        if len(self.floors) <= 1:
            return

        # Clean up ESCALATOR_UP on the floor just below the top
        floor_below = self.floors[-2]
        for row in floor_below:
            for col_idx, tile in enumerate(row):
                if tile == ESCALATOR_UP:
                    row[col_idx] = EMPTY

        # Remove the top floor
        self.floors.pop()

        # If the player was viewing the removed floor, pull them down
        self.current_floor = min(self.current_floor, len(self.floors) - 1)

    def switch_floor(self, index):
        if 0 <= index < len(self.floors):
            self.current_floor = index

    def get_current(self):
        return self.floors[self.current_floor]