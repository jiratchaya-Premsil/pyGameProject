import pygame
import random

class Boid:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))

    def update(self):
        self.pos += self.vel

        # simple boundary bounce
        if self.pos.x < 0 or self.pos.x > 1000:
            self.vel.x *= -1
        if self.pos.y < 0 or self.pos.y > 700:
            self.vel.y *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 100, 100), (int(self.pos.x), int(self.pos.y)), 3)