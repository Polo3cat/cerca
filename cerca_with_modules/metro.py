from geodesics import haversine_distance
from tuples import MetroDistance


def get_closest_stops(reference, stops, radius, size):
    result = []
    for stop in stops:
        distance = int(haversine_distance(reference.latitude, reference.longitude, stop.point.latitude,
                                          stop.point.longitude))
        if distance <= radius:
            result.append(MetroDistance(stop.name, distance))
    sorted_result = sorted(result, key=lambda s: s.distance)
    return sorted_result[0:size]

