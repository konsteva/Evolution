
from dataclasses import dataclass
import math
import random

from cell import Cell
from genome import Genome


@dataclass
class DeadCell:
    x: float
    y: float
    radius: float
    energy: float
    genome: object
    age: float = 0.0


class Environment:

    def __init__(
            self,
            width: float,
            height: float,
            energy_system,
            metabolism_rate: float = 0.01,
            movement_cost: float = 0.01,
            turn_probability: float = 0.1,
            max_turn_angle: float = 0.5,
            decomposition_time: float = 100.0,
            generation_probability: float = 0.001,
            generation_energy: float = 20.0,
            initial_cell_radius=2.0,
            initial_cell_speed=1.0,
            rng=None
    ):

        self.width = width
        self.height = height

        self.energy_system = energy_system

        self.cells = []
        self.dead_cells = []

        self.time = 0.0
        self.steps = 0

        # Simulation parameters
        self.metabolism_rate = metabolism_rate
        self.movement_cost = movement_cost

        self.turn_probability = turn_probability
        self.max_turn_angle = max_turn_angle

        self.decomposition_time = decomposition_time

        self.generation_probability = generation_probability
        self.generation_energy = generation_energy

        self.initial_cell_radius = initial_cell_radius
        self.initial_cell_speed = initial_cell_speed

        self.rng = rng or random.Random()

        if width <= 0 or height <= 0:
            raise ValueError("World dimensions must be positive.")

        self._validate_parameters()

    def _validate_parameters(self):
        if not math.isfinite(self.metabolism_rate) or self.metabolism_rate < 0:
            raise ValueError("Invalid metabolism rate.")

        if not math.isfinite(self.movement_cost) or self.movement_cost < 0:
            raise ValueError("Invalid movement cost.")

        if not 0 <= self.turn_probability <= 1:
            raise ValueError("Invalid turn probability.")

        if not math.isfinite(self.max_turn_angle) or self.max_turn_angle < 0:
            raise ValueError("Invalid turn angle.")

        if not math.isfinite(self.decomposition_time) or self.decomposition_time <= 0:
            raise ValueError("Invalid decomposition time.")

        if not 0 <= self.generation_probability <= 1:
            raise ValueError("Invalid generation probability.")

        if not math.isfinite(self.generation_energy) or self.generation_energy <= 0:
            raise ValueError("Invalid generation energy.")

    # --------------------------------------------------
    # CELL MANAGEMENT
    # --------------------------------------------------

    def create_cell(self, x, y, energy, radius=None, speed=None, direction=None, genome=None):
        """Create a cell using environmental energy."""

        if direction is None:
            direction = self.rng.uniform(0, 2 * math.pi)

        if radius is None:
            radius = self.initial_cell_radius

        if speed is None:
            speed = self.initial_cell_speed

        cell = Cell.spawn(
            energy_system=self.energy_system,
            x=x % self.width,
            y=y % self.height,
            initial_energy=energy,
            radius=radius,
            speed=speed,
            direction=direction,
            genome=genome or Genome()
        )

        self.cells.append(cell)

        return cell

    def kill_cell(self, cell):
        """Kill a cell and transfer its remaining energy to dead energy."""

        if cell not in self.cells or not cell.alive:
            return

        remaining_energy = cell.energy

        cell.die(self.energy_system)

        self.dead_cells.append(
            DeadCell(
                x=cell.x,
                y=cell.y,
                radius=cell.radius,
                energy=remaining_energy,
                genome=cell.genome
            )
        )

        self.cells.remove(cell)

    # --------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------

    def move_cell(self, cell, dt):
        """Move a cell using blind, probabilistic movement."""

        if not cell.alive:
            return

        # Randomly change direction
        if self.rng.random() < self.turn_probability:
            turn = self.rng.uniform(
                -self.max_turn_angle,
                self.max_turn_angle
            )

            cell.direction = (
                                     cell.direction + turn
                             ) % (2 * math.pi)

        # Calculate displacement
        distance = cell.speed * dt

        dx = math.cos(cell.direction) * distance
        dy = math.sin(cell.direction) * distance

        # Toroidal boundaries
        cell.x = (cell.x + dx) % self.width
        cell.y = (cell.y + dy) % self.height

        # Movement energy expenditure
        cost = distance * self.movement_cost

        self._expend_cell_energy(cell, cost)

    # --------------------------------------------------
    # ENERGY
    # --------------------------------------------------

    def _expend_cell_energy(self, cell, amount):
        """Expend energy without allowing negative energy."""

        if not cell.alive:
            return

        amount = min(amount, cell.energy)

        if amount > 0:
            cell.expend_energy(self.energy_system, amount)

        if not cell.alive:
            self._register_dead_cell(cell)

    def _register_dead_cell(self, cell):
        """Register a cell that has died from energy depletion."""

        if cell in self.cells:
            self.dead_cells.append(
                DeadCell(
                    x=cell.x,
                    y=cell.y,
                    radius=cell.radius,
                    energy=0.0,
                    genome=cell.genome
                )
            )

            self.cells.remove(cell)

    def metabolize(self, cell, dt):
        """Continuous metabolic energy expenditure."""

        cost = self.metabolism_rate * dt

        self._expend_cell_energy(cell, cost)

    # --------------------------------------------------
    # SPATIAL INTERACTIONS
    # --------------------------------------------------

    def distance_between(self, a, b):
        """Calculate shortest distance with toroidal boundaries."""

        dx = abs(a.x - b.x)
        dy = abs(a.y - b.y)

        dx = min(dx, self.width - dx)
        dy = min(dy, self.height - dy)

        return math.sqrt(dx * dx + dy * dy)

    def detect_contacts(self):
        """Return all pairs of living cells in physical contact."""

        contacts = []

        for i in range(len(self.cells)):
            for j in range(i + 1, len(self.cells)):

                a = self.cells[i]
                b = self.cells[j]

                distance = self.distance_between(a, b)

                if distance <= a.radius + b.radius:
                    contacts.append((a, b))

        return contacts

    # --------------------------------------------------
    # DECOMPOSITION
    # --------------------------------------------------

    def decompose(self, dt):
        """Return residual dead-cell energy to the environment."""

        remaining_dead_cells = []

        for dead in self.dead_cells:

            dead.age += dt

            if dead.age >= self.decomposition_time:

                if dead.energy > 0:
                    self.energy_system.transfer(
                        "dead",
                        "environment",
                        dead.energy
                    )

            else:
                remaining_dead_cells.append(dead)

        self.dead_cells = remaining_dead_cells

    # --------------------------------------------------
    # SPONTANEOUS GENERATION
    # --------------------------------------------------

    def spontaneous_generation(self):
        """Generate a new cell using environmental energy."""

        if self.rng.random() >= self.generation_probability:
            return None

        if self.energy_system.environmental_energy < self.generation_energy:
            return None

        x = self.rng.uniform(0, self.width)
        y = self.rng.uniform(0, self.height)

        return self.create_cell(
            x=x,
            y=y,
            energy=self.generation_energy
        )

    # --------------------------------------------------
    # SIMULATION
    # --------------------------------------------------

    def step(self, dt=1.0):
        """Advance the simulation by one time step."""

        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be positive and finite.")

        # 1. Move cells
        for cell in self.cells.copy():
            self.move_cell(cell, dt)

        # 2. Metabolism
        for cell in self.cells.copy():
            self.metabolize(cell, dt)

        # 3. Detect physical contacts
        contacts = self.detect_contacts()

        # Interactions will be implemented later.

        # 4. Spontaneous generation
        self.spontaneous_generation()

        # 5. Decomposition
        self.decompose(dt)

        # 6. Update time
        self.time += dt
        self.steps += 1

        # 7. Verify energy conservation
        self.assert_energy_conservation()

        if not self.cells:
            print("All cells have died. Simulation ended.")
            return None

        return contacts

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def assert_energy_conservation(self):
        """Verify the global energy invariant."""

        living_energy = sum(cell.energy for cell in self.cells)

        dead_energy = sum(dead.energy for dead in self.dead_cells)

        if not math.isclose(
                living_energy,
                self.energy_system.living_energy,
                rel_tol=1e-9,
                abs_tol=1e-7
        ):
            raise AssertionError(
                f"Living energy accounting mismatch! "
                f"Cells: {living_energy:.12f}, "
                f"Ledger: {self.energy_system.living_energy:.12f}, "
                f"Difference: {living_energy - self.energy_system.living_energy:.12f}"
            )

        if not math.isclose(
                dead_energy,
                self.energy_system.dead_energy,
                rel_tol=1e-9,
                abs_tol=1e-7
        ):
            raise AssertionError(
                f"Dead energy accounting mismatch! "
                f"Dead cells: {dead_energy:.12f}, "
                f"Ledger: {self.energy_system.dead_energy:.12f}, "
                f"Difference: {dead_energy - self.energy_system.dead_energy:.12f}"
            )

        self.energy_system.assert_conservation()
