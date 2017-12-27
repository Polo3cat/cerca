# Code adapted from Chris Veness work, free to use, under MIT License:
# https://www.movable-type.co.uk/scripts/latlong.html
import math


def haversine_distance(latitude1, longitude1, latitude2, longitude2):
    radius = 6371000
    phi1 = math.radians(latitude1)
    phi2 = math.radians(latitude2)
    delta_phi = math.radians(latitude2 - latitude1)
    delta_lambda = math.radians(longitude2 - longitude1)

    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) \
        + math.cos(phi1) * math.cos(phi2) \
        * math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d
