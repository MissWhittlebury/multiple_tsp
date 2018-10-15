"""
Module to make requests to Bing Maps' API.
"""
import requests

# URL to Bing's distance matrix API
_base_url = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?'


def get_distance_matrix(origin_lat, origin_lon, dest_lat, dest_lon, bing_api_key):
    """
    Gets the driving distance from the origin coordinates to the destination coordinates.

    :param origin_lat: float, the latitude of the location you are traveling from.
    :param origin_lon: float, the longitude of the location you are traveling from.
    :param dest_lat: float, the latitude of the location you are traveling to.
    :param dest_lat: float, the longitude of the location you are traveling to.
    :param bing_api_key: str, the Bing Maps API key used to make the request to
        Bing Maps' distance matrix API.

    :return: response object, will return none if request didn't return a status
        code of 200 or the response object if it did.
    """
    result = None
    args = 'origins={o_lat},{o_lon}&destinations={d_lat},{d_lon}&travelMode=driving&distanceUnit=mi&key={key}'\
            .format(o_lat=origin_lat, o_lon=origin_lon,
                    d_lat=dest_lat,   d_lon=dest_lon,
                    key=bing_api_key)
    url = _base_url + args
    resp = requests.get(url)
    if resp.status_code == 200:
        result = resp

    return result


def get_distance(origin_lat, origin_lon, dest_lat, dest_lon, bing_api_key):
    """
    This function is used to extract the 'travelDistance' from the response
    object returned from the get_distance_matrix function.

    :param origin_lat: float, the latitude of the location you are traveling from.
    :param origin_lon: float, the longitude of the location you are traveling from.
    :param dest_lat: float, the latitude of the location you are traveling to.
    :param dest_lat: float, the longitude of the location you are traveling to.
    :param bing_api_key: str, the Bing Maps API key used to make the request to
        Bing Maps' distance matrix API.

    :return: float, will return none if get_distance_matrix returns none, otherwise will return the driving distance in miles from the origin to the destination.
    """
    distance = None
    resp = get_distance_matrix(origin_lat, origin_lon, dest_lat, dest_lon, bing_api_key)
    if resp:
        resp_dict = resp.json()
        distance = resp_dict['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']

    return distance