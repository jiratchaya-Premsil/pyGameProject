import pygame
from config import *
from core.floor_manager import FloorManager
from editor.grid_editor import GridEditior
from simulation.boid_manager import BoidManager

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mall Layout Simulator")

        self.clock = pygame.time.Clock()

        self.floor_manager = FloorManager()
        self.editor = GridEditior(self.floor_manager)
        self.boids = BoidManager(self.floor_manager)

        self.running = True
        self.show_simulation = True  # Start with simulation enabled
        self.font = pygame.font.SysFont("consolas", 20)

        self.show_grid = True

        self.add_floor_button = pygame.Rect(10, 40 + 4 * 25, 125, 30)
        self.prev_floor_button = pygame.Rect(130, 40 + 4 * 25, 125, 30)
        self.next_floor_button = pygame.Rect(250, 40 + 4 * 25, 125, 30)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.editor.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.show_simulation = not self.show_simulation

                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid

                if event.key == pygame.K_q:
                    self.floor_manager.current_floor -= 1

                if event.key == pygame.K_e:
                    self.floor_manager.current_floor += 1

                self.floor_manager.current_floor = max(
                    0,
                    min(self.floor_manager.current_floor,
                        len(self.floor_manager.floors)-1)
                )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.add_floor_button.collidepoint(event.pos):
                    self.floor_manager.add_floor()
                elif self.prev_floor_button.collidepoint(event.pos):
                    if self.floor_manager.current_floor > 0:
                        self.floor_manager.current_floor -= 1
                elif self.next_floor_button.collidepoint(event.pos):
                    if self.floor_manager.current_floor < len(self.floor_manager.floors) - 1:
                        self.floor_manager.current_floor += 1
    def update(self):
        if self.show_simulation:
            self.boids.update()

        # Decrement error timer
        if self.editor.error_timer > 0:
            self.editor.error_timer -= 1
        else:
            self.editor.error_message = None

    def draw(self):
        self.screen.fill((30, 30, 30))

        self.editor.draw(self.screen)

        if self.show_simulation:
            self.boids.draw(self.screen)
        if self.show_grid:
            self.editor.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()


    def draw_ui(self):

        floor_text = f"Floor: {self.floor_manager.current_floor + 1}"
        Max_FloorText = f"Max Floor: {len(self.floor_manager.floors)}"
        tile_names = {
            0: "EMPTY",
            1: "WALKABLE",
            2: "STORE",
            3: "ESCALATOR_UP",
            4: "ESCALATOR_DOWN",
            5: "DOOR"
        }

        tile_text = f"Tile: {tile_names.get(self.editor.current_tile, 'UNKNOWN')}"
        grid_text = f"Grid: {'ON' if self.show_grid else 'OFF'}"
        sim_text = f"Simulation: {'ON' if self.show_simulation else 'OFF'} ({len(self.boids.boids)} boids)"

        texts = [floor_text, Max_FloorText, tile_text, grid_text, sim_text]

        for i, txt in enumerate(texts):
            surface = self.font.render(txt, True, (255,255,255))
            self.screen.blit(surface, (10, 10 + i*25))

        pygame.draw.rect(self.screen, (100, 100, 100), self.add_floor_button)
        button_text = self.font.render("Add Floor", True, (255, 255, 255))
        self.screen.blit(button_text, (self.add_floor_button.x + 5, self.add_floor_button.y + 5))

        pygame.draw.rect(self.screen, (100, 100, 100), self.prev_floor_button)
        prev_text = self.font.render("Prev Floor", True, (255, 255, 255))
        self.screen.blit(prev_text, (self.prev_floor_button.x + 5, self.prev_floor_button.y + 5))

        pygame.draw.rect(self.screen, (100, 100, 100), self.next_floor_button)
        next_text = self.font.render("Next Floor", True, (255, 255, 255))
        self.screen.blit(next_text, (self.next_floor_button.x + 5, self.next_floor_button.y + 5))

        # Display error message if any
        if self.editor.error_message:
            error_surface = self.font.render(self.editor.error_message, True, (255, 0, 0))
            self.screen.blit(error_surface, (10, HEIGHT - 30))