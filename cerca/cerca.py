import argparse
import ast
import webbrowser
from argparse import ArgumentParser, RawTextHelpFormatter
import math
import re
from collections import namedtuple
from datetime import datetime, timedelta
from urllib.request import urlopen
from xml.etree import ElementTree
import unicodedata


TABLE_TEMPLATE = '''
<table>
    {0}
</table>
'''

INSIDE_TABLE = '''
<tr>
    <th class="activitat" colspan="2">Activitat</th>
</tr>
<tr>
    <td colspan="2">{0.name}</td>     
</tr>
<tr>
    <th class="info">Lloc</th>
    <th class="info">Direcció</th>
    <th class="info">Numero</th>
    <th class="info">Dia</th>
    <th class="info">Hora</th>
    <th class="info">Edat</th>
</tr>
<tr>
    <td>{0.place}</td>
    <td>{0.address}</td>
    <td>{0.number}</td>
    <td>{0.day}</td>
    <td>{0.hour}</td>
    <td>{0.age}</td>
</tr>
{1}
'''

STATIONS_ROW = '''
<tr>
    <th class="stops">Estació</th>
    <th class="stops">Distància (metres)</th>
</tr>'''

STATIONS_TEMPLATE = '''
<tr>
    <td>{0.name}</td>
    <td>{0.distance}</td>
</tr>'''

HTML_DOC_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Query Results</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
{0}
</body>
</html>'''

CSS_DOC = '''

table {
    color: #333;
    font-family: Helvetica, Arial, sans-serif;
    width: 640px; 
    border-collapse: collapse; 
    border-spacing: 0; 
}
th, td {
    border: 1px solid #CCC; 
    height: 30px;
}
th {
    background: #DFDFDF;
    font-weight: bold;
}
td {
    background: #FAFAFA;
    text-align: center;
}
.activitat {
    background-color: #595959;
    color: white;
    width: 8%;
}
.info {
    background-color: #878787;
    color: black;
    width: 8%;
}
.stops {
    background-color: #adadad;
    color: black;
    width: 8%;
}
'''

KEY_HELP = '''Either a string, a list, a tuple or a list with any combination
of the three previous. All elements in a list will be satisfied. One of the 
elements in a tuple will be satisfied. Strings are case insensitive and 
diacritics are ignored. Must go inside single quotes and each string surrounded
by double quotes.
E.g:
'"park"'
'["park","clown","chocolate"]'
'("dog","cat")'
'["balloon",("football","basket")]' '''

DATE_HELP = '''dd/mm/yyyy format. Either a date, a tuple with a date a low range
and an upper range or a list combining any of the previous. Must go inside single 
quotes.
E.g:
'01/06/2017'
'(24/09/2017,-3,1)'
'[03/01/2017,(06/01/2017,-1,1),(14/01/2017,0,1)]' '''

METRO_HELP = '''"L#" represents a metro line, being # any number. On its own, a 
list, a tuple or a list combining any of the previous elements. All elements in 
a list will be satisfied. One of the elements in a tuple will be satisfied. 
Must go inside single quotes.
E.g:
'[L1,L5]'
'[L11]'
'[(L3,L5),L4]' '''

MetroStop = namedtuple('MetroStop', 'name point')
Point = namedtuple('Point', 'latitude longitude')
MetroDistance = namedtuple('MetroDistance', 'name distance')
Activity = namedtuple('Activity', 'name place address number day hour age')
Result = namedtuple('Result', 'activity stations')


def interpret_key(string):
    interpretation = ast.literal_eval(string)
    if isinstance(interpretation, str) or isinstance(interpretation, tuple) or isinstance(interpretation, list):
        return interpretation
    msg = '%r is not a valid key' % string
    argparse.ArgumentTypeError(msg)


def interpret_date(string):
    dates = re.findall('[0-3][0-9]/[0-1][0-9]/[0-9]{4}(?!,-[0-9]+,[0-9]+)', string)
    date_tuples = re.findall('\([0-3][0-9]/[0-1][0-9]/[0-9]{4},-[0-9]+,[0-9]+\)', string)
    date_list = []
    for date in dates:
        date_list.append(datetime.strptime(date, '%d/%m/%Y'))
    for date_tuple in date_tuples:
        base_date = re.search('[0-3][0-9]/[0-1][0-9]/[0-9]{4}', date_tuple).group(0)
        negative_delta = int(re.search('(?<=[0-3][0-9]/[0-1][0-9]/[0-9]{4},)-?[0-9]+', date_tuple).group(0))
        positive_delta = int(re.search("[0-9]+(?=\))", date_tuple).group(0))
        date_list.append(datetime.strptime(base_date, '%d/%m/%Y'))
        for delta in range(1, positive_delta + 1):
            date_list.append(datetime.strptime(base_date, '%d/%m/%Y') + timedelta(days=delta))
        for delta in range(-1, negative_delta - 1, -1):
            date_list.append(datetime.strptime(base_date, '%d/%m/%Y') + timedelta(days=delta))
    if date_list:
        return date_list
    else:
        msg = '%r is not a valid date' % string
        argparse.ArgumentTypeError(msg)


def interpret_metro(string):
    no_l = string.replace('L', '')
    interpretation = ast.literal_eval(no_l)
    if isinstance(interpretation, int) or isinstance(interpretation, tuple) or isinstance(interpretation, list):
        return interpretation
    msg = '%r is not a valid metro' % string
    argparse.ArgumentTypeError(msg)


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


def get_closest_stops(reference, stops, radius, size):
    result = []
    for stop in stops:
        distance = int(haversine_distance(reference.latitude, reference.longitude, stop.point.latitude,
                                          stop.point.longitude))
        if distance <= radius:
            result.append(MetroDistance(stop.name, distance))
    sorted_result = sorted(result, key=lambda s: s.distance)
    return sorted_result[0:size]


def output_results(results):
    inside_content = ''
    for result in results:
        stations = ''
        for station in result.stations:
            stations += STATIONS_TEMPLATE.format(station)
        if stations != '':
            stations = STATIONS_ROW + stations
        inside_content += INSIDE_TABLE.format(result.activity, stations)
    if inside_content == '':
        inside_content = 'No s\'han trobat resultats'
    table = TABLE_TEMPLATE.format(inside_content)
    page = HTML_DOC_TEMPLATE.format(table)
    css = CSS_DOC
    f = open('style.css', 'w')
    f.write(css)
    f.close()
    g = open('result.html', 'w')
    g.write(page)
    g.close()
    webbrowser.open_new_tab('result.html')


def get_age(event):
    classificacions = event.find('classificacions')
    ages = []
    for nivell in classificacions:
        if 'anys' in nivell.text:
            text = nivell.text.replace('de', '')
            text = text.replace('anys', '')
            if text[0] == '+':
                ages.append(100)
            else:
                pos_a = text.find('a')
                ages.append(int(text[0:pos_a]))
                ages.append(int(text[pos_a+1:]))
    if not ages:
        return '-'
    elif min(ages) == max(ages):
        return '+12 anys'
    else:
        min_age = min(ages)
        max_age = max(ages)
        return '{0} a {1} anys'.format(min_age, '+12') if max_age == 100 else '{0} a {1} anys'.format(min_age, max_age)


def get_event_info(event):
    name = event.find('nom').text
    place = event.find('lloc_simple').find('nom').text
    address = event.find('lloc_simple').find('adreca_simple').find('carrer').text
    number = event.find('lloc_simple').find('adreca_simple').find('numero').text
    date = event.find('data').find('data_proper_acte').text
    day = date[0:10]
    hour = date[11:]
    age = get_age(event)
    return Activity(name, place, address, number, day, hour, age)


def get_event_coordinates(event):
    attributes = event.find('lloc_simple').find('adreca_simple').find('coordenades').find('googleMaps').attrib
    latitude = float(attributes.get('lat'))
    longitude = float(attributes.get('lon'))
    return Point(latitude, longitude)


def normalize(string):
    return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn')).casefold()


def get_encoding(raw_declaration):
    decoded_declaration = raw_declaration.decode('utf-8')
    split_declaration = decoded_declaration.split()
    for attribute in split_declaration:
        if attribute[0:8] == 'encoding':
            return attribute[10:-1]
    return 'utf-8'  # default encoding


def follows_date_restrictions(date, date_mask):
    for mask in date_mask:
        if date == mask:
            return True
    return False


def follows_keys_restrictions(combined_keys, key_mask):
    if isinstance(key_mask, str):
        normalized_mask = normalize(key_mask)
        if normalized_mask in combined_keys:
            return True
        return False
    if isinstance(key_mask, list):
        for condition in key_mask:
            if not follows_keys_restrictions(combined_keys, condition):
                return False
        return True
    if isinstance(key_mask, tuple):
        for condition in key_mask:
            if follows_keys_restrictions(combined_keys, condition):
                return True
        return False


def follows_metro_restrictions(metro_number, metro_mask):
    if isinstance(metro_mask, int):
        if metro_number == metro_mask:
            return True
        return False
    if isinstance(metro_mask, list):
        for condition in metro_mask:
            if not follows_metro_restrictions(metro_number, condition):
                return False
        return True
    if isinstance(metro_mask, tuple):
        for condition in metro_mask:
            if follows_metro_restrictions(metro_number, condition):
                return True
        return False


def get_keys(acte):
    keys = ''
    if acte.find('nom').text:
        keys = keys + ' ' + acte.find('nom').text
    if acte.find('lloc_simple').find('nom').text:
        keys = keys + ' ' + acte.find('lloc_simple').find('nom').text
    if acte.find('lloc_simple').find('adreca_simple').find('barri').text:
        keys = keys + ' ' + acte.find('lloc_simple').find('adreca_simple').find('barri').text
    if acte.find('lloc_simple').find('adreca_simple').find('barri').text:
        keys = keys + ' ' + acte.find('lloc_simple').find('adreca_simple').find('carrer').text
    return keys


def has_coordinates(acte):
    coord = acte.find('lloc_simple').find('adreca_simple').find('coordenades').find('googleMaps').attrib
    try:
        float(coord.get('lat'))
        float(coord.get('lon'))
        return True
    except ValueError:
        return False


def is_infantil(acte):
    classificacions = acte.find('classificacions')
    for nivell in classificacions:
        if 'infants' in nivell.text or 'anys' in nivell.text:
            return True
    return False


class XMLScraperInterface:

    def __init__(self):
        self._page = None

    def set_page(self, url):
        content = urlopen(url).read()
        encoding = get_encoding(content[0:200])
        decoded = content.decode(encoding=encoding)
        root = ElementTree.fromstring(decoded)
        self._page = root


class XMLScraperFilterInterface(XMLScraperInterface):

    def get_filtered_elements(self):
        raise NotImplementedError

    def _has_restrictions(self, element):
        raise NotImplementedError


class XMLScraperKeysDates(XMLScraperFilterInterface):

    def __init__(self, keys, dates):
        super().__init__()
        self._key_mask = keys
        self._date_mask = dates

    def get_filtered_elements(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self._has_restrictions(acte) and has_coordinates(acte) and is_infantil(acte))

    def _has_restrictions(self, element):
        keys = get_keys(element)
        normalized_keys = normalize(keys)
        if follows_keys_restrictions(normalized_keys, self._key_mask):
            if element.find('data').find('data_proper_acte').text:
                date = element.find('data').find('data_proper_acte').text
                formatted_date = datetime.strptime(date[0:10], '%d/%m/%Y')
                if follows_date_restrictions(formatted_date, self._date_mask):
                    return True
        return False


class XMLScraperKeys(XMLScraperFilterInterface):

    def __init__(self, keys):
        super().__init__()
        self._key_mask = keys

    def get_filtered_elements(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self._has_restrictions(acte) and has_coordinates(acte) and is_infantil(acte))

    def _has_restrictions(self, element):
        keys = get_keys(element)
        normalized_keys = normalize(keys)
        if follows_keys_restrictions(normalized_keys, self._key_mask):
            if element.find('data').find('data_proper_acte').text:
                return True
        return False


class XMLScraperDates(XMLScraperFilterInterface):

    def __init__(self, dates):
        super().__init__()
        self._date_mask = dates

    def get_filtered_elements(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self._has_restrictions(acte) and has_coordinates(acte) and is_infantil(acte))

    def _has_restrictions(self, element):
        if element.find('data').find('data_proper_acte').text:
            date = element.find('data').find('data_proper_acte').text
            formatted_date = datetime.strptime(date[0:10], '%d/%m/%Y')
            if follows_date_restrictions(formatted_date, self._date_mask):
                return True
        return False


class XMLScraperNoFilter(XMLScraperInterface):

    def get_filtered_elements(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if has_coordinates(acte) and is_infantil(acte))


class XMLScraperMetro(XMLScraperInterface):

    def __init__(self):
        super().__init__()

    def get_metro_stops(self):
        ls = []
        punts = self._page.findall('Punt')
        for punt in punts:
            if punt.find('Coord').find('Latitud').text \
                    and punt.find('Coord').find('Longitud').text \
                    and punt.find('Tooltip').text and self._has_restrictions(punt):
                lat = float(punt.find('Coord').find('Latitud').text)
                long = float(punt.find('Coord').find('Longitud').text)
                name = punt.find('Tooltip').text[0:-1]
                ls.append(MetroStop(name, Point(lat, long)))
        return ls

    def _has_restrictions(self, element):
        tooltip = element.find('Tooltip').text
        match = re.search('METRO', tooltip)
        if not match:
            return False
        else:
            return True


class XMLScraperMetroFilter(XMLScraperFilterInterface):

    def __init__(self, metro_mask):
        super().__init__()
        self._metro_mask = metro_mask

    def get_metro_stops(self):
        return self.get_filtered_elements()

    def get_filtered_elements(self):
        ls = []
        punts = self._page.findall('Punt')
        for punt in punts:
            if punt.find('Coord').find('Latitud').text \
                    and punt.find('Coord').find('Longitud').text \
                    and punt.find('Tooltip').text and self._has_restrictions(punt):
                lat = float(punt.find('Coord').find('Latitud').text)
                long = float(punt.find('Coord').find('Longitud').text)
                name = punt.find('Tooltip').text[0:-1]
                ls.append(MetroStop(name, Point(lat, long)))
        return ls

    def _has_restrictions(self, element):
        tooltip = element.find('Tooltip').text
        match_line = re.findall('L[0-9][0-9]?', tooltip)
        match_metro = re.findall('METRO', tooltip)
        if not match_metro or not match_line:
            return False
        else:
            for line in match_line:
                metro_number = int(line[1:])
                if follows_metro_restrictions(metro_number, self._metro_mask):
                    return True
            return False


def main():
    cli_parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    cli_parser.add_argument('--key', type=interpret_key, help=KEY_HELP)
    cli_parser.add_argument('--date', type=interpret_date, help=DATE_HELP)
    cli_parser.add_argument('--metro', type=interpret_metro, help=METRO_HELP)
    arguments = vars(cli_parser.parse_args())

    if arguments.get('key') and arguments.get('date'):
        xml_scraper = XMLScraperKeysDates(arguments.get('key'), arguments.get('date'))
    elif arguments.get('key'):
        xml_scraper = XMLScraperKeys(arguments.get('key'))
    elif arguments.get('date'):
        xml_scraper = XMLScraperDates(arguments.get('date'))
    else:
        xml_scraper = XMLScraperNoFilter()

    xml_scraper.set_page('http://w10.bcn.es/APPS/asiasiacache/peticioXmlAsia?id=199')
    filtered_events = xml_scraper.get_filtered_elements()

    if arguments.get('metro'):
        metro_xml_scraper = XMLScraperMetroFilter(arguments.get('metro'))
    else:
        metro_xml_scraper = XMLScraperMetro()
    metro_xml_scraper.set_page('http://opendata-ajuntament.barcelona.cat/resources/bcn/TRANSPORTS%20GEOXML.xml')
    metro_stops = metro_xml_scraper.get_metro_stops()
    results = []
    for event in filtered_events:
        reference = get_event_coordinates(event)
        closest_stops = get_closest_stops(reference, metro_stops, 500, 5)
        activity = get_event_info(event)
        results.append(Result(activity, closest_stops))
    output_results(results)


if __name__ == "__main__":
    main()

