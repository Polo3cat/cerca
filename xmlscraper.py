import xml.etree.ElementTree as ElementTree

import requests
import unicodedata

from datetime import datetime


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


class XMLScraperInterface:
    def __init__(self):
        self._page = None

    def set_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            encoding = get_encoding(content[0:200])
            decoded = content.decode(encoding=encoding)
            root = ElementTree.fromstring(decoded)
            self._page = root
        except requests.exceptions.RequestException as e:
            print(e)

    def get_filtered_events(self):
        raise NotImplementedError

    def has_restrictions(self, acte):
        raise NotImplementedError


class XMLScraperKeysDates(XMLScraperInterface):

    def __init__(self, keys, dates):
        super().__init__()
        self._key_mask = keys
        self._date_mask = dates

    def get_filtered_events(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self.has_restrictions(acte))

    def has_restrictions(self, acte):
        keys = get_keys(acte)
        normalized_keys = normalize(keys)
        if follows_keys_restrictions(normalized_keys, self._key_mask):
            if acte.find('data').find('data_proper_acte').text:
                date = acte.find('data').find('data_proper_acte').text
                formatted_date = datetime.strptime(date[0:10], '%d/%m/%Y')
                if follows_date_restrictions(formatted_date, self._date_mask):
                    return True
        return False


class XMLScraperKeys(XMLScraperInterface):

    def __init__(self, keys):
        super().__init__()
        self._key_mask = keys

    def get_filtered_events(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self.has_restrictions(acte))

    def has_restrictions(self, acte):
        keys = get_keys(acte)
        normalized_keys = normalize(keys)
        if follows_keys_restrictions(normalized_keys, self._key_mask):
            if acte.find('data').find('data_proper_acte').text:
                return True
        return False


class XMLScraperDates(XMLScraperInterface):

    def __init__(self, dates):
        super().__init__()
        self._date_mask = dates

    def get_filtered_events(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes if self.has_restrictions(acte))

    def has_restrictions(self, acte):
        if acte.find('data').find('data_proper_acte').text:
            date = acte.find('data').find('data_proper_acte').text
            formatted_date = datetime.strptime(date[0:10], '%d/%m/%Y')
            if follows_date_restrictions(formatted_date, self._date_mask):
                return True
        return False


class XMLScraperNoFilter(XMLScraperInterface):

    def get_filtered_events(self):
        actes = self._page.find('body').find('resultat').find('actes')
        return (acte for acte in actes)
