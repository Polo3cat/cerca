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
