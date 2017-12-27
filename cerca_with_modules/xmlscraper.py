import xml.etree.ElementTree as ElementTree

import re
from urllib.request import urlopen

import unicodedata

from datetime import datetime

from tuples import Point, MetroStop, Activity


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
