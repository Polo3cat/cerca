import argparse
import ast

from datetime import datetime, timedelta

import re


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
            date_list.append(datetime.strptime(base_date, '%d/%m/%Y')+timedelta(days=delta))
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
