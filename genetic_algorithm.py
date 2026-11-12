import random
import config
import entities

class GeneticAlgorithm:
	def __init__(self, mutation_rate=None, mutation_sigma=None):
		self.mutation_rate = mutation_rate
		self.mutation_sigma = mutation_sigma

	def selection(self, population):
		# Get top 50% individual bird have best fitness
		sorted_pop = sorted(population, key=lambda b: b.fitness, reverse=True)
		survivors_bird = sorted_pop[:len(sorted_pop) // 2]
		return survivors_bird

	def crossover(self, parent_dad, parent_mom):
		# Crossover: get random each gene from dad and mama
		child_chromosome = []
		for i in range(len(parent_dad.chromosome)):
			c_min = min(parent_dad.chromosome[i], parent_mom.chromosome[i])
			c_max = max(parent_dad.chromosome[i], parent_mom.chromosome[i])
			d = c_max - c_min
			min_val = c_min - 0.2 * d
			max_val = c_max + 0.2 * d
			child_chromosome.append(random.uniform(min_val, max_val))
		return child_chromosome

	def mutate(self, child_chromosome, mutation_rate, mutation_sigma):
		# Mutation gene: ech gene have 10% opportunity for small change
		for i in range(len(child_chromosome)):
			if random.uniform(0, 1) < mutation_rate:
				child_chromosome[i] += random.gauss(mu=0.0, sigma=mutation_sigma)
		return child_chromosome

	def next_generation(self, population):
		# Create new generation from present population

		# 1. Get best birds from population
		survivors = self.selection(population)
		next_gene = []

		# Auto get LinearBird or MlpBird
		bird_cls = type(survivors[0])
		pop_size = len(population)

		if bird_cls == entities.MlpBird:
			rate = self.mutation_rate if self.mutation_rate is not None else config.MlpConfig.MUTATION_RATE
			sigma = self.mutation_sigma if self.mutation_sigma is not None else config.MlpConfig.MUTATION_SIGMA
		else:
			rate = self.mutation_rate if self.mutation_rate is not None else config.LinearConfig.MUTATION_RATE
			sigma = self.mutation_sigma if self.mutation_sigma is not None else config.LinearConfig.MUTATION_SIGMA

		# 2. Keep the best individual bird (elitism)
		best_bird = survivors[0]
		elite = bird_cls(y=config.BIRD_START_Y, chromosome=best_bird.chromosome)
		next_gene.append(elite)

		# 3. Create the remaining offstring using crossover + mutate
		while len(next_gene) < pop_size:
			parent_dad = random.choice(survivors)
			parent_mom = random.choice(survivors)
			if len(survivors) > 1:
				while parent_dad == parent_mom:
					parent_mom = random.choice(survivors)
			child_chrom = self.crossover(parent_dad, parent_mom)
			child_chrom = self.mutate(child_chrom, mutation_rate=rate, mutation_sigma=sigma)
			child = bird_cls(y=config.BIRD_START_Y, chromosome=child_chrom)
			next_gene.append(child)
		return next_gene