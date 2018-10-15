"""
Objects needed to store, manage, create, breed, and mutate routes.
"""
import random


class Route:
    """
    This object will manage a set of Truck objects and their corresponding routes.
    """
    def __init__(self, number_of_trucks, distance_df, origin):
        """
        :param number_of_trucks: int, the number of trucks available to go on a 
            route.
        :param distance_df: DataFrame, a distance matrix in the form of a pandas
            DataFrame used to calculate distances between locations.
        :param origin: str, name of the origin location used in the distance matrix.
        """
        self.number_of_trucks = number_of_trucks
        self.distance_df      = distance_df
        self.origin           = origin
        self.stops            = [s for s in distance_df.index if s != origin]
        
        self.trucks           = self._create_trucks()
        self.total_distance   = 0
        self.fitness          = 0
        self.chunk_size       = int(len(self.stops) * .10)


    def _create_trucks(self):
        """
        Will create all of the Truck objects prescribed by the number_of_trucks
        attribute with a random number of stops given to each Truck. The total 
        number of stops for all of the Truck objects will be the number of 
        non-origin locations in the distance_df.

        :return: list, a list of the Truck objects created.
        """
        number_of_stops_available = len(self.stops)
        trucks = []
        for t in range(self.number_of_trucks):
            if (t + 1) != self.number_of_trucks:
                number_of_stops = random.randrange(0,number_of_stops_available)
                truck = Truck(number_of_stops)
                trucks.append(truck)
                number_of_stops_available -= number_of_stops
            else:
                number_of_stops = number_of_stops_available
                truck = Truck(number_of_stops)
                trucks.append(truck)

        return trucks


    def create_routes(self):
        """
        Calls the create_route attribute for each Truck. Will manage the stops 
        available to each Truck route creation so no stop is stopped at by more
        than one Truck route. This method will create the routes randomly. This 
        differs from the breed_routes method which will create Truck routes based
        on two Route objects.
        
        :return: list, the Truck objects managed by the Route.
        """
        stops_available = [s for s in self.stops]
        for t in self.trucks:
            route = t.create_route(stops_available)
            for r in route:
                stops_available.remove(r)

        return self.trucks


    def breed_routes(self, parent1, parent2):
        """
        Will create Truck routes based on the Truck routes of two other Route 
        objects. The basis of the Truck routes will be the parent1. A part of the
        parent1 Truck routes will get replaced by a chunk of the parent2 Truck 
        routes. Each stop will still only be stopped at once.

        :param parent1: Route object, the basis of the Truck routes for this
            Route object.
        :param parent2: Route object, the route of the Trucks are used to adjust
            the Truck routes from the parent1 Truck routes.

        :return: list of lists, the routes of each Truck.
        """
        parent1_routes = parent1.get_routes()
        parent2_routes = parent2.get_routes()
        routes = self._adjust_routes(parent1_routes, parent2_routes)
        for i,t in enumerate(self.trucks):
            t.route = routes[i]

        return routes


    def _adjust_routes(self, routes1, routes2):
        """
        Takes two lists of routes and replaces part of the first set of routes
        with part of the second set of routes. Will ensure that each location is
        only stopped at once.

        :param routes1: list of lists, the Truck routes of all trucks in a Route
            object.
        :param routes2: list of lists, same as routes1 variable.

        :return: list of lists, the adjusted routes of input routes.
        """
        routes = routes1
        chunk_size = self._determine_chunk_size(routes1, routes2)
        r1_chunk, r1_route_idx, r1_chunk_idx = self._get_chunk(routes1, chunk_size)
        r2_chunk, r2_route_idx, r2_chunk_idx = self._get_chunk(routes2, chunk_size)

        ##get indices of items in chunk2
        replace_dest = []
        for idx_r, r in enumerate(routes):
            for idx_d, d in enumerate(r):
                if d in r2_chunk:
                    replace_dest.append((idx_r,idx_d,d))

        ##replace chunk1 with chunk2
        for i,idx in enumerate(range(r1_chunk_idx[0], r1_chunk_idx[1])):
            routes[r1_route_idx][idx] = r2_chunk[i]

        ##get destinations that are the same in both chunks
        dup_dest = set(r1_chunk).intersection(r2_chunk)

        ##remove the tuples from replace_dest list where the names are duplicates
        dedupe_replace_dest = [i for i in replace_dest if i[2] not in dup_dest]

        ##remove the values from r1_chunk where the names are duplicates
        for d in dup_dest:
            r1_chunk.remove(d)

        ##put destinations back in route somewhere
        for i,v in enumerate(dedupe_replace_dest):
            routes[v[0]][v[1]] = r1_chunk[i]

        return routes


    def _determine_chunk_size(self, routes1, routes2):
        """
        Used by the _adjust_routes method to determine the number of consecutive
        destinations to take from routes2 and replace in routes1. This is needed
        to ensure that the size of the chunk swapped is not larger than a route
        in either set of routes.

        :param routes1: list of lists, the Truck routes of all trucks in a Route
            object.
        :param routes2: list of lists, same as routes1 variable.

        :return: int, the size of the chunk to be swapped in the Truck routes.        
        """
        chunk_size = self.chunk_size
        for r in routes1:
            if len(r) < chunk_size and len(r) != 0:
                chunk_size = len(r)
        
        for r in routes2:
            if len(r) < chunk_size and len(r) != 0:
                chunk_size = len(r)

        return chunk_size


    def _get_chunk(self, routes, chunk_size):
        """
        Used by _adjust_routes method to actually get the chunk to be replaced 
        in a set of routes.

        :param routes: list of lists, the Truck routes of all trucks in a Route
            object.
        :param chunk_size: int, the size of the chunk that needs to be swapped 
             in the routes variable.

        :return chunk: list, a list of consecutive locations from the routes that
            will be replaced.
        :return route_idx: int, the index of the list in the routes list where 
            the chunk is located.
        :return chunk_idx: tuple, the beginning and end point of the chunk in the
            route.
        """
        chunk_routes = [i for i,r in enumerate(routes) if len(r) > 0]
        route_idx = random.choice(chunk_routes)
        chunk = routes[route_idx]
        max_start = len(chunk) - chunk_size
        if max_start == 0:
            start = 0
        else:
            start = random.randrange(0, max_start)
        
        end       = start + chunk_size
        chunk     = chunk[start:end]
        chunk_idx = (start, end)

        return chunk, route_idx, chunk_idx


    def mutate(self, mutation_rate):
        """
        Will swap two random locations in the Truck routes. The swap will only
        occur if a randomly generated number between 0 and 1 is less than the
        mutaion_rate variable.

        :param mutaion_rate: float, between 0 and 1. Ideally this is the percent 
            of Route objects taht will have their Truck routes adjusted.
        """
        #TODO: consider adding mutation that moves one item to another place, no swap.
        if random.random() < mutation_rate:
            routes = self.get_routes()
            routes = self._swap_mutation(routes)
            for i,t in enumerate(self.trucks):
                t.route = routes[i]
        

    def _swap_mutation(self, routes):
        """
        Used by the mutate method. This does the actual swap of two locations 
        and returns the set of routes.

        :param routes: list of list, the Truck routes of the current Route object.

        :return: list of lists, the Truck routes with two locations swapped.
        """
        routes_to_mutate = [i for i,v in enumerate(routes) if len(v) > 0]

        idx1 = [random.choice(routes_to_mutate)]
        idx1.append(random.randrange(len(routes[idx1[0]])))
        item1 = routes[idx1[0]][idx1[1]]

        idx2 = [random.choice(routes_to_mutate)]
        idx2.append(random.randrange(len(routes[idx2[0]])))
        item2 = routes[idx2[0]][idx2[1]]

        routes[idx1[0]][idx1[1]] = item2
        routes[idx2[0]][idx2[1]] = item1

        return routes


    def get_routes(self):
        """
        Retrieves and returns the routes of each truck in the current Route object.

        :return: list of lists, the route of each Truck managed by the object.
        """
        routes = []
        for t in self.trucks:
            route = [d for d in t.route]
            routes.append(route)

        return routes


    def calculate_distance(self):
        """
        Will calculate the toal distance traveled by all Truck objects to complete
        their routes. The distance includes the Truck beginning and ending its 
        route at the origin.

        :return: float, the toal distance traveled for each location to be 
            stopped at once.
        """
        self.total_distance = 0
        for t in self.trucks:
            if len(t.route) > 0:
                for i in range(len(t.route) + 1):
                    if i == 0:
                        self.total_distance += float(self.distance_df.loc[self.origin, t.route[i]])
                    elif i == len(t.route):
                        self.total_distance += float(self.distance_df.loc[t.route[i-1], self.origin])
                    else:
                        self.total_distance += float(self.distance_df.loc[t.route[i-1], t.route[i]])

        return self.total_distance


    def calculate_fitness(self, distance):
        ## Note: This is currently unused
        if self.total_distance != 0:
            self.fitness = 1 / float(self.total_distance)

        return self.fitness



class Truck:
    """
    An object used to hold a route. The create_route method is only used to randomly create a route based on the number_of_stops variable. Otherwise the Route object will adjust the route of a Truck.
    """
    def __init__(self, number_of_stops):
        """
        :param number_of_stops: int, the number of stops that this Truck will
        make. This variable is only used if a route needs to be randomly created
        for the truck. Otherwise this attribute will not be descriptive of the
        actual route variable.
        """
        self.number_of_stops = number_of_stops

        self.route = None

    def create_route(self, stops_available):
        """
        Randomly creates a route based on the stops_available. Only used to
        create the initial population.

        :param stops_available: list, a list of stops that still need to visited
            by a Truck. This length of this list must be greater than the
            number_of_stops attribute.
        """
        if self.route is None:
            self.route = random.sample(stops_available, self.number_of_stops)
        
        return self.route
