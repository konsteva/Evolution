
from energy_system import EnergySystem
from environment import Environment
from vizualization.renderer import Renderer


def main():

    energy = EnergySystem(
        environmental_energy=10000
    )

    world = Environment(
        width=100,
        height=100,
        energy_system=energy,
        initial_cell_radius=0.5,
        initial_cell_speed=1.0
    )

    # Initial population
    for _ in range(20):

        world.create_cell(
            x=world.rng.uniform(0, world.width),
            y=world.rng.uniform(0, world.height),
            # radius=0.5,
            energy=100
        )

    # Start visualization
    renderer = Renderer(world)

    renderer.run(dt=1.0, fps=60)


if __name__ == "__main__":
    main()
