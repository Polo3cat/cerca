from argparse import ArgumentParser, RawTextHelpFormatter

import interpreter
from metro import get_closest_stops
from templates import KEY_HELP, DATE_HELP, METRO_HELP
from tuples import Result
from webgenerator import output_results
from xmlscraper import XMLScraperKeysDates, XMLScraperKeys, XMLScraperDates, XMLScraperNoFilter, XMLScraperMetro, \
    get_event_coordinates, XMLScraperMetroFilter, get_event_info


def main():
    cli_parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    cli_parser.add_argument('--key', type=interpreter.interpret_key, help=KEY_HELP)
    cli_parser.add_argument('--date', type=interpreter.interpret_date, help=DATE_HELP)
    cli_parser.add_argument('--metro', type=interpreter.interpret_metro, help=METRO_HELP)
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
