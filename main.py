from argparse import ArgumentParser

import interpreter
from xmlscraper import XMLScraperKeysDates, XMLScraperKeys, XMLScraperDates, XMLScraperNoFilter


def main():
    cli_parser = ArgumentParser()
    cli_parser.add_argument('--key', type=interpreter.interpret_key)
    cli_parser.add_argument('--date', type=interpreter.interpret_date)
    cli_parser.add_argument('--metro', type=interpreter.interpret_metro)
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
    filtered_events = xml_scraper.get_filtered_events()
    print(list(filtered_events))


if __name__ == "__main__":
    main()
