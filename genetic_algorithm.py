import random

import config
import brain
import entities

# --- Built Geenetic algorithm
class GeneticAlgorithm:
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

	def mutate(self, child_chromosome, mutation_rate=0.1):
		# Mutation gene: ech gene have 10% opportunity for small change
		for i in range(len(child_chromosome)):
			if random.uniform(0, 1) < mutation_rate:
				child_chromosome[i] += random.gauss(mu=0.0, sigma=config.MUTATION_SIGMA)
		return child_chromosome

	def nex_generation(self, population):
		# Create new generation from present population

		# 1. Get best birds from population
		survivors = self.selection(population)
		next_generation = []

		# 2. Keep the best individual bird (elitism)
		best_bird = survivors[0]
		elite = entities.Bird(config.BIRD_START_Y)
		elite.chromosome = list(best_bird.chromosome)
		next_generation.append(elite)

		# 3. Create the remaining offstring using crossover + mutate
		while len(next_generation) < config.POP_SIZE:
			# Choose random father and mother from survivors
			parent_dad = random.choice(survivors)
			parent_mom = random.choice(survivors)

			# Check
			if len(survivors) > 1:
				while parent_dad == parent_mom:
					parent_mom = random.choice(survivors)

			child = entities.Bird(config.BIRD_START_Y)
			child.chromosome = self.crossover(parent_dad, parent_mom)
			child.chromosome = self.mutate(child.chromosome)
			next_generation.append(child)
		
		return next_generation

