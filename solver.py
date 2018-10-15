"""
High level functions that implement the genetic algorithm. These functions will
perform the tasks of creating the initial randomized population, selecting the
mating pool for consecutive generations, breeding a generation from a mating
pool, and mutating a new generation.
"""
import random
import route

##Solver variables that can be adjusted to better help the algorithm converge on a solution
_population_size = 250
_generations     = 500
_percent_elite   = .20
_mutation_rate   = .35

_elite_size      = int(_population_size * _percent_elite)


def create_initial_population(number_of_trucks, distance_df, origin):
    """
    Creates an initial population of Route objects with randomized routes.

    :param number_of_trucks: int, the number of trucks that can be used to stop 
        at all locations.
    :param distance_df: pandas DataFrame, distance matrix that includes all
        locations that need to be stopped at.
    :param origin: str, name of the origin location in the distance_df.

    :return: list, a list of all Route objects created.
    """
    population = []
    for i in range(_population_size):
        current_route = route.Route(number_of_trucks, distance_df, origin)
        current_route.create_routes()
        population.append(current_route)

    return population


def rank_population(population):
    """
    Will rank the Route objects from shortest distance required to stop at all 
    locations to longest distance.

    :param population: list, all the Route objects that are part of the current 
        generation.

    :return: list, all the Route objects in the current generation sorted from 
        shortest to longest distance.
    """
    ranked_pop = []
    for p in population:
        current_route = (p, p.calculate_distance())
        ranked_pop.append(current_route)

    ranked_pop.sort(key=lambda r: r[1])

    return ranked_pop


def select_weighted_random_route(ranked_pop):
    """
    Used by the parent_selection function to choose a random Route from the
    ranked population. Items ranked higher have a greater chance of being
    selected than lower ranked items. 
    
    :param ranked_pop: list, the Route objects ranked from shortest to longest
        distance.

    :return: Route object, a randomly chosed Route object.
    """
    result = None
    max_pick = random.randrange(2,_population_size)
    result = random.choice(ranked_pop[:max_pick])
    result = result[0]

    return result


def parent_selection(ranked_pop):
    """
    Creates a mating pool for the next generation based on the current
    population. Will always keep a top percentage (aka elite) of Route objects of a
    population. The size of the "elite" population is based on the
    _percent_elite variable. The remainder of the mating pool is created based
    on weighted random selection.

    :param ranked_pop: list, the Route objects ranked from shortest to longest
        distance.

    :return: list, the list of Route objects that will be used to create the next generation of Route objects. There can and probably will be duplicates of Route objects in the mating pool. This is fine cause better Route objects should have a higher chance of breeding future Route objects.
    """
    mating_pool = []
    for i in range(_elite_size):
        mating_pool.append(ranked_pop[i][0])

    for i in range(_population_size - _elite_size):
        parent = select_weighted_random_route(ranked_pop)
        mating_pool.append(parent)

    return mating_pool


def breed_population(mating_pool, number_of_trucks, distance_df, origin):
    """
    Will breed a new generation from the mating pool. Ensures that a percent of
    the best Route objects will make it into new generation. The remainder of
    the generation has two randomly chosen parent Route objects that are used to
    breed a new child Route object.

    :param mating_pool: list, a list of the objects that are available to be
        chosen as parents. The function will assume that the necessary number of
        Elite Route objects are the first items in the list.
    :param number_of_trucks: int, the number of trucks that can be used to stop 
        at all locations.
    :param distance_df: pandas DataFrame, distance matrix that includes all
        locations that need to be stopped at.
    :param origin: str, name of the origin location in the distance_df.

    :return: list, the list of Route objects to be used as the new population.
    """
    new_population = []
    shuffled_pool  = random.sample(mating_pool, _population_size)

    ##maintain elite objects
    for i in range(_elite_size):
        elite_route = mating_pool[i]
        new_population.append(elite_route)

    for i in range(_population_size - _elite_size):
        parent_route1 = shuffled_pool[i]
        parent_route2 = shuffled_pool[_population_size-i-1]
        child_route   = route.Route(number_of_trucks, distance_df, origin)
        child_route.breed_routes(parent_route1, parent_route2)
        new_population.append(child_route)

    return new_population


def mutate_population(new_population):
    """
    Calls the mutate method on all Route objects in the provided list. This will
    randomly mutate Route objects of the new population.
    """
    mutated_pop = []
    for r in new_population:
        r.mutate(_mutation_rate)
        mutated_pop.append(r)

    return mutated_pop


def new_population(population, number_of_trucks, distance_df, origin):
    """
    Goes through the necessary steps to create the next generation from the
    current population. Ranks the current population, selects the mating pool,
    breeds the next generation, mutates the generation. 
 
    :param population: list, all of the Route objects in the current population.
    :param number_of_trucks: int, the number of trucks that can be used to stop 
        at all locations.
    :param distance_df: pandas DataFrame, distance matrix that includes all
        locations that need to be stopped at.
    :param origin: str, name of the origin location in the distance_df.

    :return: list, the Route objects of the next generation.
   """
    ranked_pop = rank_population(population)
    mating_pool = parent_selection(ranked_pop)
    new_population = breed_population(mating_pool, number_of_trucks, distance_df, origin)
    new_population = mutate_population(new_population)

    return new_population


def find_best_route(number_of_trucks, distance_df, origin):
    """
    The high level genetic algorithm function. This will go through the number
    of generations in the _generations variable, returning the best Route object
    in the final generation.

    :param number_of_trucks: int, the number of trucks that can be used to stop 
        at all locations.
    :param distance_df: pandas DataFrame, distance matrix that includes all
        locations that need to be stopped at.
    :param origin: str, name of the origin location in the distance_df.

    :return shortest_distance: float, the distance in miles of the shortest route.
    :return best_route: list of lists, the routes of each Truck for the best
        Route object.
    """
    population = create_initial_population(number_of_trucks, distance_df, origin)

    for i in range(_generations):
        population = new_population(population, number_of_trucks, distance_df, origin)
        shortest_distance, best_route = get_best_route(population)
        print(best_route)
        print(shortest_distance)

    shortest_distance, best_route = get_best_route(population)
    return shortest_distance, best_route


def get_best_route(population):
    """
    Chooses the best (aka the Route object with the shortest total_distance
    attribute) Route the provided population.

    :return shortest_distance: float, the distance in miles of the shortest route.
    :return best_route: list of lists, the routes of each Truck for the best
        Route object.
    """

    shortest_distance = 0
    best_route = None
    for r in population:
        distance = r.calculate_distance()
        if distance < shortest_distance or shortest_distance == 0:
            shortest_distance = distance
            best_route = r.get_routes()

    return shortest_distance, best_route