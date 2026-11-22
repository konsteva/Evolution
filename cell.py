
from dataclasses import dataclass
import math


@dataclass
class Cell:
    x: float
    y: float
    radius: float
    speed: float
    direction: float
    energy: float
    genome: object = None
    age: float = 0.0
    alive: bool = True

    @classmethod
    def spawn(
            cls,
            energy_system,
            x: float,
            y: float,
            initial_energy: float,
            radius: float = 2.0,
            speed: float = 1.0,
            direction: float = 0.0,
            genome=None
    ):
        """Create a cell using energy from the environment."""

        if not math.isfinite(initial_energy) or initial_energy <= 0:
            raise ValueError("Initial energy must be positive.")

        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("Position must be finite.")

        if not math.isfinite(radius) or radius <= 0:
            raise ValueError("Radius must be positive.")

        if not math.isfinite(speed) or speed < 0:
            raise ValueError("Speed must be non-negative.")

        if not math.isfinite(direction):
            raise ValueError("Direction must be finite.")

        energy_system.transfer(
            "environment", "living", initial_energy
        )

        return cls(
            x=x,
            y=y,
            radius=radius,
            speed=speed,
            direction=direction % (2 * math.pi),
            energy=initial_energy,
            genome=genome
        )

    def expend_energy(self, energy_system, amount: float):
        """Transfer energy from this cell to the environment."""

        self._require_alive()

        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Energy expenditure must be non-negative.")

        if amount > self.energy:
            raise ValueError("Insufficient cell energy.")

        energy_system.transfer("living", "environment", amount)
        self.energy -= amount

        if self.energy == 0:
            self.die(energy_system)

    def transfer_energy_to(self, other, amount: float):
        """Transfer energy between two living cells."""

        self._require_alive()
        other._require_alive()

        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Transfer amount must be non-negative.")

        if amount > self.energy:
            raise ValueError("Insufficient cell energy.")

        self.energy -= amount
        other.energy += amount

        if self.energy == 0:
            # Zero-energy cells die without residual energy.
            self.alive = False

    def die(self, energy_system):
        """Move remaining cell energy into the dead reservoir."""

        self._require_alive()

        if self.energy > 0:
            energy_system.transfer(
                "living", "dead", self.energy
            )

        self.energy = 0.0
        self.alive = False

    def advance_age(self, dt: float):
        """Advance the cell's age by a time interval."""

        self._require_alive()

        if not math.isfinite(dt) or dt < 0:
            raise ValueError("Time interval must be non-negative.")

        self.age += dt

    def _require_alive(self):
        if not self.alive:
            raise RuntimeError("Cell is not alive.")
