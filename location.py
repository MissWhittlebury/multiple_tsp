"""
Location object to hold data on each location. Mainly needed to hold the distance
from the given location to all other locations.
"""
import distance


class Location:
    """
    Location object composed of the given location and a dictionary of distances
    to all other locations added via add_destination method.
    """
    def __init__(self, name, latitude, longitude):
        """
        :param name: str, the name used to identify this location.
        :param latitude: float, the latitude of the location.
        :param longitude: float, the longitude of the location.
        """
        self.name      = name
        self.latitude  = latitude
        self.longitude = longitude

        self.origin    = False
        self.destinations = {}


    def add_destination(self, name, latitude, longitude, bing_api_key):
        """
        Will append the given destination to the destination dictionary attribute 
        with name and distance from Location object to destination.

        :param name: str, the name used to identify the destination.
        :param latitude: float, the latitude of the destination.
        :param longitude: float, the longitude of the destination.
        :param bing_api_key: str, the Bing Maps API key used to make the request
          to Bing Maps' distance matrix API

        :return: float, the distance in miles from the Location to the given
          coordinates.
        """
        dest_distance = distance.get_distance(origin_lat=self.latitude,
                                              origin_lon=self.longitude,
                                              dest_lat=latitude,
                                              dest_lon=longitude,
                                              bing_api_key=bing_api_key)
        self.destinations[name] = dest_distance

        return dest_distance
