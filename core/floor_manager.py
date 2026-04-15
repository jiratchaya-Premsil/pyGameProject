from config import *

class FloorManager:
    def __init__(self):
        self.floors = [self.create_floor()]
        self.current_floor = 0

    def create_floor(self):
        cols = 1000 // GRID_SIZE
        rows = 700 // GRID_SIZE
        return [[EMPTY for _ in range(cols)] for _ in range(rows)]

    def add_floor(self):
        self.floors.append(self.create_floor())
    def switch_floor(self,index):
        if 0 <= index < len(self.floors):
            self.current_floor = index
    def get_current(self):
        return self.floors[self.current_floor]
