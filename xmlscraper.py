import xml.etree.ElementTree as ElementTree

import requests
import unicodedata


def get_encoding(raw_declaration):
    decoded_declaration = raw_declaration.decode('utf-8')
    split_declaration = decoded_declaration.split()
    for attribute in split_declaration:
        if attribute[0:8] == 'encoding':
            return attribute[10:-1]
    return 'utf-8'  # default encoding


def key_restrictions(combined_keys, key_mask):
    if key_mask is str:
        if key_mask in combined_keys:
            return True
        return False
    if key_mask is list:
        for condition in key_mask:
            if not key_restrictions(combined_keys, condition):
                return False
        return True
    if key_mask is tuple:
        for condition in key_mask:
            if key_restrictions(combined_keys, condition):
                return True
        return False


def has_restrictions(acte, key_mask, date_mask):
    nom = acte.find('nom').text
    lloc = acte.find('lloc_simple').find('nom').text
    barri = acte.find('lloc_simple').find('adreca_simple').find('barri').text
    keys = nom + ' ' + lloc + ' ' + barri
    if key_restrictions(keys, key_mask):
        return True
    else:
        return False


class XMLScraper:
    def __init__(self):
        self._pages = {}

    def add_page(self, url, name):
        response = requests.get(url)
        content = response.content
        encoding = get_encoding(content[0:200])
        decoded = content.decode(encoding=encoding)
        root = ElementTree.fromstring(decoded)
        self._pages.update({name: root})

    def filter_key_date(self, page, key_mask, date_mask):
        actes = self._pages.get(page).find('body').find('resultat').find('actes')
        return (acte for acte in actes if has_restrictions(acte, key_mask, date_mask))
