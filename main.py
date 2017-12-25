from argparse import ArgumentParser

import interpreter
from xmlscraper import XMLScraper


def main():
    cli_parser = ArgumentParser()
    cli_parser.add_argument('--key', type=interpreter.interpret_key)
    cli_parser.add_argument('--date', type=interpreter.interpret_date)
    cli_parser.add_argument('--metro', type=interpreter.interpret_metro)
    arguments = vars(cli_parser.parse_args())

    xml_scraper = XMLScraper()
    xml_scraper.add_page('http://w10.bcn.es/APPS/asiasiacache/peticioXmlAsia?id=199', 'events')
    xml_scraper.add_page('http://opendata-ajuntament.barcelona.cat/resources/bcn/TRANSPORTS%20GEOXML.xml', 'transport')

    filtered_events = xml_scraper.filter_key_date('events', arguments.get('key'), arguments.get('date'))
    print(list(filtered_events))


if __name__ == "__main__":
    main()
