
from dataclasses import dataclass, field
import copy
import random


DEFAULT_MUTATION_RATES = {
    "identity": 0.05,
    "parameter": 0.05,
    "parameter_add": 0.01,
    "parameter_remove": 0.01,
    "gene_insert": 0.01,
    "gene_delete": 0.01,
    "gene_duplicate": 0.01,
    "gene_rearrange": 0.01,
    "rate_mutation": 0.005,
}


@dataclass
class Gene:
    identity: float
    parameters: list[float] = field(default_factory=list)
    activation_conditions: list = field(default_factory=list)


@dataclass
class Genome:
    genes: list[Gene] = field(default_factory=list)

    mutation_rates: dict[str, float] = field(
        default_factory=lambda: DEFAULT_MUTATION_RATES.copy()
    )

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Check genome structure and mutation rates."""

        for gene in self.genes:
            if not isinstance(gene, Gene):
                raise ValueError("Genome must contain Gene objects.")

            if not isinstance(gene.identity, (int, float)):
                raise ValueError("Gene identity must be numerical.")

            if any(not isinstance(p, (int, float))
                   for p in gene.parameters):
                raise ValueError("Gene parameters must be numerical.")

        for name, rate in self.mutation_rates.items():
            if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
                raise ValueError(f"Invalid mutation rate: {name}")

    def copy(self):
        """Create an independent copy of the genome."""
        return copy.deepcopy(self)

    def mutate(
            self,
            rng=None,
            identity_step=0.05,
            parameter_step=0.1,
            rate_step=0.005
    ):
        """Return a mutated copy without modifying the parent."""

        rng = rng or random.Random()
        offspring = self.copy()

        # 1. Gene-level mutations
        for gene in offspring.genes:

            if rng.random() < offspring.mutation_rates["identity"]:
                gene.identity += rng.gauss(0, identity_step)

            for i in range(len(gene.parameters)):
                if rng.random() < offspring.mutation_rates["parameter"]:
                    gene.parameters[i] += rng.gauss(
                        0, parameter_step
                    )

            # Parameter insertion
            if rng.random() < offspring.mutation_rates["parameter_add"]:
                gene.parameters.append(rng.gauss(0, 1))

            # Parameter deletion
            if gene.parameters and rng.random() < offspring.mutation_rates["parameter_remove"]:
                index = rng.randrange(len(gene.parameters))
                gene.parameters.pop(index)

        # 2. Structural mutations

        # Gene insertion
        if rng.random() < offspring.mutation_rates["gene_insert"]:
            new_gene = Gene(
                identity=rng.gauss(0, 1),
                parameters=[rng.gauss(0, 1)]
            )
            index = rng.randrange(len(offspring.genes) + 1)
            offspring.genes.insert(index, new_gene)

        # Gene deletion
        if offspring.genes and rng.random() < offspring.mutation_rates["gene_delete"]:
            index = rng.randrange(len(offspring.genes))
            offspring.genes.pop(index)

        # Gene duplication
        if offspring.genes and rng.random() < offspring.mutation_rates["gene_duplicate"]:
            index = rng.randrange(len(offspring.genes))
            duplicate = copy.deepcopy(offspring.genes[index])
            offspring.genes.insert(index + 1, duplicate)

        # Gene rearrangement
        if len(offspring.genes) > 1 and rng.random() < offspring.mutation_rates["gene_rearrange"]:
            i, j = rng.sample(range(len(offspring.genes)), 2)
            offspring.genes[i], offspring.genes[j] = (
                offspring.genes[j],
                offspring.genes[i]
            )

        # 3. Mutation rates themselves can evolve
        for name in offspring.mutation_rates:
            if rng.random() < offspring.mutation_rates["rate_mutation"]:
                offspring.mutation_rates[name] += rng.gauss(
                    0, rate_step
                )

                offspring.mutation_rates[name] = max(
                    0.0,
                    min(1.0, offspring.mutation_rates[name])
                )

        offspring.validate()
        return offspring
