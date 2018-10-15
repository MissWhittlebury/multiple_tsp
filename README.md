# Solving Multiple Traveling Salesperson with a Genetic Algorithm
<br>
<br>

## Overview
<br>
To solve the multiple traveling salesperson problem the process first determines the distance from each location (including the origin) to every possible location. This is done by making requests to the Bing Maps Distance Matrix API. Once the results have been collected a distance matrix is outputted in the form of a csv to limit the number of API calls required.
<br>
<br>
The process then moves on to optimizing the routes for the specified number of drivers by implementing a genetic algorithm. The basic constraints applied to the algorithm are that each truck must begin and end at the origin location and every location listed must be stopped at only once. The algorithm is implemented by creating an initial random population of routes. A mating pool is created from the current population by selecting the "elite" routes (defined as the routes with the shortest total distance traveled) and doing weighted random selection of the other members of the population. The shorter routes have a better chance of getting randomly selected for the the mating pool. The routes are then used to create the next population by choosing the "elite" routes and "breeding" the remaining routes from the mating pool. "Mutations" are injected into the population at random before the new generation is finished. This process is repeated for the set number of generations. When the final generation has finished the best route is exported into the provided csv filename and the total distance for the route is printed to the screen.
<br>
<br>
Although the process has only been tested for two drivers, it could theoretically handle as many drives as requested of it by simply changing the variable that holds the number of drivers. The one caveat is that the way the code was written could cause errors if only one driver is used.
<br>
<br>
While the algorithm works it still struggles for consistency, and optimization amongst the solver variables. These variables are available in the solver.py script and can be adjusted as needed. With that being said, the solver will consistently converge on a final route that deviates about 5% in total distance. While the paths may differ amongst the optimized routes, the small range of distances helps increases confidence that the algorithm "works".
<br>
<br>
<br>
<br>

## Arguments and Sample Calls
<br>
* -f FILENAME, Name of the file that includes all delivery locations. Columns must be in the following order: name, address, latitude, longitude. The address column does not need to be populated. The first row of the file needs to be a header.
* -k KEY, The key to be used for the Bing Maps Distance Matrix API requests.
* -om OUTPUTMATRIX, Filename for the distance matrix csv.
* -m MATRIX, Filename of a previously created distance matrix. This argument can be used to run just the solver portion of the script without wasting API requests.
* -r RESULT, Filename for the best route created by the genetic algorithm.
<br>
<br>
Sample Calls:
* python main.py -f Location_Coords.csv -k this_is_your_bing_api_key -om Distance_Matrix.csv -r Best_Route.csv
* python main.py -m Distance_Matrix.csv -r Best_Route.csv
<br>
<br>
Note: Every call must have either the -f, -k, -om combination of arguments or just the -m argument.
<br>
<br>
<br>
<br>

## Future Improvements/Updates
<br>
* Unit tests
* Add ability to make batch API calls to get the distance from a Location to all destinations.
* Improve the mating pool selection because it too heavily weights higher ranked routes even if they are only slightly better than the worst routes. This increases the risk of ending at a local optimum. The parent_selection function could also be revisted to limit convergence on a local optimum.
* Add a mutation method where a swap doesn't occur. Just the movement of a single location to another point.
* Single truck and greater than two truck solution testing
* Allow option to run the routes without starting and ending at origin. This could be nice if you want to optimize 3 circles (ex. multiple bar crawls)
* Allow option to require each truck to make the same number of stops
<br>
<br>
<br>
<br>

### Changelog
