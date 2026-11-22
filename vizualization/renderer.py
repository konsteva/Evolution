
import pygame


class Renderer:

    def __init__(
            self,
            environment,
            window_width=1000,
            window_height=800,
            background=(18, 20, 24)
    ):
        pygame.init()

        self.environment = environment

        self.window_width = window_width
        self.window_height = window_height

        self.screen = pygame.display.set_mode(
            (window_width, window_height)
        )

        pygame.display.set_caption("Artificial Life Simulation")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)

        self.background = background

        self.running = True
        self.paused = False

        self.simulation_speed = 1.0

        # Colors
        self.cell_color = (100, 200, 130)
        self.dead_color = (100, 105, 110)
        self.outline_color = (210, 220, 215)
        self.text_color = (220, 220, 220)

    def draw_cell(self, cell):
        """Draw a living cell."""

        scale_x = self.window_width / self.environment.width
        scale_y = self.window_height / self.environment.height

        x = int(cell.x * scale_x)
        y = int(cell.y * scale_y)

        radius = max(
            1,
            int(cell.radius * min(scale_x, scale_y))
        )

        pygame.draw.circle(
            self.screen,
            self.cell_color,
            (x, y),
            radius
        )

        pygame.draw.circle(
            self.screen,
            self.outline_color,
            (x, y),
            radius,
            width=1
        )

    def draw_dead_cell(self, cell):
        """Draw a dead cell."""

        scale_x = self.window_width / self.environment.width
        scale_y = self.window_height / self.environment.height

        x = int(cell.x * scale_x)
        y = int(cell.y * scale_y)

        radius = max(
            1,
            int(cell.radius * min(scale_x, scale_y))
        )

        pygame.draw.circle(
            self.screen,
            self.dead_color,
            (x, y),
            radius
        )

    def draw_information(self):
        """Display simulation statistics."""

        energy = self.environment.energy_system

        information = [
            f"Time: {self.environment.time:.1f}",
            f"Steps: {self.environment.steps}",
            f"Living cells: {len(self.environment.cells)}",
            f"Dead cells: {len(self.environment.dead_cells)}",
            f"Environmental energy: {energy.environmental_energy:.1f}",
            f"Living energy: {energy.living_energy:.1f}",
            f"Dead energy: {energy.dead_energy:.1f}",
            f"Total energy: {energy.total_energy:.1f}",
            f"Speed: {self.simulation_speed:.1f}x",
            "SPACE: Pause | UP/DOWN: Speed | ESC: Exit"
        ]

        for i, text in enumerate(information):

            surface = self.font.render(
                text,
                True,
                self.text_color
            )

            self.screen.blit(
                surface,
                (12, 12 + i * 21)
            )

    def render(self):
        """Render one frame."""

        self.screen.fill(self.background)

        for cell in self.environment.dead_cells:
            self.draw_dead_cell(cell)

        for cell in self.environment.cells:
            self.draw_cell(cell)

        self.draw_information()

        pygame.display.flip()

    def handle_events(self):
        """Handle user input."""

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                elif event.key == pygame.K_UP:
                    self.simulation_speed = min(
                        20.0,
                        self.simulation_speed * 2
                    )

                elif event.key == pygame.K_DOWN:
                    self.simulation_speed = max(
                        0.125,
                        self.simulation_speed / 2
                    )

    def run(self, dt=1.0, fps=60):
        """Run the visualization and simulation."""

        while self.running:

            self.handle_events()

            if not self.paused:

                steps = max(
                    1,
                    int(self.simulation_speed)
                )

                step_dt = (
                        dt * self.simulation_speed / steps
                )

                for _ in range(steps):
                    result = self.environment.step(step_dt)

                    if result is None and not self.environment.cells:
                        self.running = False
                        break

            self.render()

            self.clock.tick(fps)

        pygame.quit()
