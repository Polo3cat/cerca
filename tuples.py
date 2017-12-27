from collections import namedtuple

MetroStop = namedtuple('MetroStop', 'name point')
Point = namedtuple('Point', 'latitude longitude')
MetroDistance = namedtuple('MetroDistance', 'name distance')
Activity = namedtuple('Activity', 'name place address number day hour age')
Result = namedtuple('Result', 'activity stations')
