import pygame
from config import *
from core.floor_manager import FloorManager
from editor.grid_editor import GridEditor
from editor.store_manager import StoreManager
from simulation.boid_manager import BoidManager


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mall Layout Simulator")

        self.clock = pygame.time.Clock()

        self.floor_manager = FloorManager()
        self.store_manager = StoreManager(self.floor_manager)
        self.editor = GridEditor(self.floor_manager, self.store_manager)
        self.boids = BoidManager(self.floor_manager)

        self.running = True
        self.sim_state = SIM_STOP   # simulation starts STOPPED

        self.show_grid = True
        self.font = pygame.font.SysFont("consolas", 18)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.sim_state == SIM_STOP:
                self.editor.handle_event(event)

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key):
        fm = self.floor_manager

        # ---- Space: toggle simulation state ----
        if key == pygame.K_SPACE:
            if self.sim_state == SIM_STOP:
                self.sim_state = SIM_START
                print("[SIM] Simulation STARTED")
            else:
                self.sim_state = SIM_STOP
                self.boids.clear()
                print("[SIM] Simulation STOPPED — all boids removed")

        # ---- Floor navigation ----
        # q / e: remove / add top floor
        if key == pygame.K_q:
            fm.remove_top_floor()
            self.store_manager.rescan()
        if key == pygame.K_e:
            fm.add_floor()
            self.store_manager.rescan()

        # a / d: go to lower / upper floor
        if key == pygame.K_a:
            fm.current_floor = max(0, fm.current_floor - 1)
        if key == pygame.K_d:
            fm.current_floor = min(len(fm.floors) - 1, fm.current_floor + 1)

        # g: toggle grid overlay
        if key == pygame.K_g:
            self.show_grid = not self.show_grid

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self):
        if self.sim_state == SIM_START:
            self.boids.update()

        if self.editor.error_timer > 0:
            self.editor.error_timer -= 1
        else:
            self.editor.error_message = None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self):
        self.screen.fill(TILES_COLORS[EMPTY])
        self.editor.draw(self.screen, self.show_grid)

        # Draw boids only while running
        if self.sim_state == SIM_START:
            self.boids.draw(self.screen)

        self.draw_ui()
        pygame.display.flip()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def draw_ui(self):
        fm = self.floor_manager
        sm = self.store_manager

        store_count    = sm.store_count()
        entrance_count = sm.entrance_count()
        exit_count     = sm.exit_count()
        boid_count     = len(self.boids.boids)
        fps            = int(self.clock.get_fps())
        tile_name      = TILES.get(self.editor.current_tile, "UNKNOWN")

        lines = [
            ("Simulation",    self.sim_state),
            ("Current Floor", str(fm.current_floor + 1)),
            ("Max Floor",     str(len(fm.floors))),
            ("Stores",        str(store_count)),
            ("Entrances",     str(entrance_count)),
            ("Exits",         str(exit_count)),
            ("Tile",          tile_name),
            ("Boids",         str(boid_count)),
            ("FPS",           str(fps)),
        ]

        # Semi-transparent panel background
        panel_w, panel_h = 260, len(lines) * 22 + 10
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        self.screen.blit(panel, (6, 6))

        # Highlight color for START state
        sim_color = (100, 255, 100) if self.sim_state == SIM_START else (255, 80, 80)

        for i, (label, value) in enumerate(lines):
            color = sim_color if label == "Simulation" else (255, 255, 255)
            text  = f"{label:<14}: {value}"
            surf  = self.font.render(text, True, color)
            self.screen.blit(surf, (12, 11 + i * 22))

        # ---- Error message ----
        if self.editor.error_message:
            err_surf = self.font.render(self.editor.error_message, True, (255, 50, 50))
            self.screen.blit(err_surf, (10, HEIGHT - 30))

        # ---- Key hints (bottom-right) ----
        hints = "[Space] Start/Stop  [Q/E] Add/Remove Floor  [A/D] Prev/Next Floor  [G] Grid  [0-6] Tile"
        hint_surf = self.font.render(hints, True, (160, 160, 160))
        self.screen.blit(hint_surf, (WIDTH - hint_surf.get_width() - 8, HEIGHT - 24))