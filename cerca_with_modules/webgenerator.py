import webbrowser

from templates import TABLE_TEMPLATE, HTML_DOC_TEMPLATE, CSS_DOC, STATIONS_TEMPLATE, STATIONS_ROW, INSIDE_TABLE


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
