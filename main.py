"""
The main script for solving the multiple traveling salesperson problem through
the use of a genetic algorithm.
"""
import argparse
import csv
import location
import pandas
import route
import solver

#A list that will be built out with all locations that need to be stopped at
_locations = []

#Hardcoded origin
_origin_name = 'Art of Pizza'
_origin_lat  = '41.937386'
_origin_lon  = '-87.668066'

#Hardcoded the number of trucks to use for problem
_number_of_trucks = 2


def blank_csv(filename):
    """
    Creates blank csv to ensure distance matrix file won't fail on file creation
    before API requests are made. Ensures API requests aren't wasted.
    """
    with open(filename, 'w', newline='') as csvfile:
        pass


def add_origin():
    """
    Adds the origin as a location that needs to be included in the distance 
    matrix.
    """
    place = location.Location(_origin_name, _origin_lat, _origin_lon)
    place.origin = True
    _locations.append(place)

    return place


def read_location_csv(filename, header):
    """
    Converts every row in the file into a location object and appends all objects
    to the _locations list.

    :param filename: str, the name of the csv with all the necessary stops. File 
        columns need to be in the following order: 
        location_name, address (doesn't need to be populated), latitude, longitude.
    :param header: boolean, True if the file has a header. Columns still need to
        be in the above prescribed order.

    :return: list, a list of every location object that was created, including 
        origin if add_origin() was run.
    """
    with open(filename, newline='') as csvfile:
        if header == True:
            next(csvfile)
        
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in file_reader:
            name = row[0]
            lat  = row[2]
            lon  = row[3]
            place = location.Location(name, lat, lon)
            _locations.append(place)

    return _locations


def add_all_destinations(bing_api_key):
    """
    Calls the add_destination() method for every location in the _location list,
    besides the objects own location.

    :param bing_api_key: str, the Bing Maps API Key needed to make requests.
    
    :return: list, the list of all locations. 
    """
    for p in _locations:
        for d in _locations:
            if p.name != d.name:
                p.add_destination(d.name, d.latitude, d.longitude, bing_api_key)

    return _locations


def distance_matrix_csv(filename):
    """
    Creates a distance matrix in a csv from the list of destinations in each
    Location object in _locations list. This file will have the distance from 
    a given location to every other location that must be visited.
    """

    def create_header_row():
        header = ['']
        for p in _locations:
            header.append(p.name)

        return header


    def create_row(place, header):
        row = []
        for d in header:
            if d == '':
                row.append(place.name)
            elif d == place.name:
                row.append(0)
            else:
                row.append(place.destinations[d])

        return row


    with open(filename, 'w', newline='') as csvfile:
        matrix_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        header = create_header_row()
        matrix_writer.writerow(header)
        for p in _locations:
            row = create_row(p, header)
            matrix_writer.writerow(row)


def read_distance_matrix_csv(filename):
    """
    Puts the distance matrix csv into a pandas dataframe so the total distance 
    of a route can be quickly calculated.
    """
    with open(filename, newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(file_reader)[1:]
        rows = {}
        for row in file_reader:
            rows[row[0]] = row[1:]
    df = pandas.DataFrame.from_dict(data=rows, orient='index', columns=header)

    return df


def best_route_csv(filename, routes):
    """
    Places the given routes into a csv with each column being a different truck's
    route and each row being the locations it must visit.

    :param filename: str, the name and location of the file to write the routes to
    :param routes: list of lists, a list of routes with each list inside the list
        representing a different truck's route.
    """
    header = []
    max_route_length = 0
    for i in range(len(routes)):
        header.append('Truck_'+str(i+1))
        route_length = len(routes[i])
        if route_length > max_route_length:
            max_route_length = route_length

    with open(filename, 'w', newline='') as csvfile:
        route_writer = csv.writer(csvfile)
        route_writer.writerow(header)
        for d in range(max_route_length):
            row = []
            for r in range(len(routes)):
                if d < len(routes[r]):
                    row.append(routes[r][d])
                else:
                    row.append('')
            route_writer.writerow(row)



if __name__ == '__main__':
    ##Arguments
    parser = argparse.ArgumentParser(description='Process to determine shortest route for two delivery trucks. The FILENAME, KEY, and OUTPUTMATRIX arguments are required unless the MATRIX argument is used.')
    parser.add_argument('-f', '--filename', type=str, help='Name of file with columns in the following order: name, address, latitude, longitude. The address column does not need to be populated. The file also needs a header.')
    parser.add_argument('-k', '--key', type=str, help='The key to be used for Bing maps API requests.')
    parser.add_argument('-om', '--outputmatrix', type=str, help='The filename to be used for the locations matrix. This is used to store API results for future use.')
    parser.add_argument('-m', '--matrix', type=str, help='Name of file with drop off locations and distance to every other location. Essentially a cached version of the distance matrix that can also be recreated from this process')
    parser.add_argument('-r', '--result', type=str, help='Name of the file to export the results to')
    args = parser.parse_args()

    ##if full run with requests
    if args.filename and args.key and args.outputmatrix:

        ##create empty csv first so you don't fail after spending API requests
        blank_csv(args.outputmatrix)

        ##add origin location
        add_origin()

        ##pull locations from csv
        read_location_csv(args.filename, header=True)

        ##add destinations for each location
        add_all_destinations(args.key)

        ##export locations and distance to destinations into csv
        distance_matrix_csv(args.outputmatrix)
 
        ##put in a pandas dataframe
        distance_df = read_distance_matrix_csv(args.outputmatrix)

    ##if just pulling from existing csv:
    elif args.matrix:
        
        ##put in pandas dataframe?
        distance_df = read_distance_matrix_csv(args.matrix)

    else:
        raise RuntimeError('The process requires the filename, key, and outputmatrix arguments or the matrix argument.')

    ##do maths and such
    shortest_distance, best_route = solver.find_best_route(number_of_trucks=_number_of_trucks,
                                                           distance_df=distance_df,
                                                           origin=_origin_name)

    ##get results
    if args.result:
        best_route_csv(args.result, best_route)


    print('best route:\n{0}'.format(best_route))
    print('total distance of route: {0}'.format(shortest_distance))        
