from simulation.boid import Boid
import random

class BoidManager:
    def __init__(self, floor_manager):
        self.floor_manager = floor_manager
        self.boids = [Boid(random.randint(0,1000), random.randint(0,700)) for _ in range(50)]

    def update(self):
        for b in self.boids:
            b.update()

    def draw(self, screen):
        for b in self.boids:
            b.draw(screen)