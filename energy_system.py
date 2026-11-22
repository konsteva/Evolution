from dataclasses import dataclass
import math


@dataclass
class EnergySystem:
    environmental_energy: float
    living_energy: float = 0.0
    dead_energy: float = 0.0

    def __post_init__(self):
        self._validate()
        self._initial_total = self.total_energy

    @property
    def total_energy(self) -> float:
        return math.fsum([
            self.environmental_energy,
            self.living_energy,
            self.dead_energy
        ])

    def transfer(self, source: str, destination: str, amount: float):
        """Transfer energy between two reservoirs."""

        reservoirs = {
            "environment": "environmental_energy",
            "living": "living_energy",
            "dead": "dead_energy"
        }

        if source not in reservoirs or destination not in reservoirs:
            raise ValueError("Invalid energy reservoir.")

        if source == destination:
            raise ValueError("Source and destination must differ.")

        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Invalid transfer amount.")

        source_attr = reservoirs[source]
        destination_attr = reservoirs[destination]

        available = getattr(self, source_attr)

        if amount > available:
            raise ValueError("Insufficient energy.")

        setattr(self, source_attr, available - amount)

        setattr(
            self,
            destination_attr,
            getattr(self, destination_attr) + amount
        )

        self.assert_conservation()

    def assert_conservation(self):
        self._validate()

        difference = self.total_energy - self._initial_total

        if not math.isclose(
                self.total_energy,
                self._initial_total,
                rel_tol=1e-9,
                abs_tol=1e-7
        ):
            raise AssertionError(
                f"Energy conservation violated! "
                f"Initial: {self._initial_total:.12f}, "
                f"Current: {self.total_energy:.12f}, "
                f"Difference: {difference:.12f}"
            )


    def _validate(self):
        values = [
            self.environmental_energy,
            self.living_energy,
            self.dead_energy
        ]

        if any(not math.isfinite(v) or v < 0 for v in values):
            raise ValueError("Energy reservoirs must be non-negative.")
