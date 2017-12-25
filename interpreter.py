import argparse
import ast

from datetime import datetime, timedelta


def interpret_key(string):
    interpretation = ast.literal_eval(string)
    if isinstance(interpretation, str) or isinstance(interpretation, tuple) or isinstance(interpretation, list):
        return interpretation
    msg = '%r is not a valid key' % string
    argparse.ArgumentTypeError(msg)


def interpret_date(string):
    if string[0] == '[':
        return interpret_date(string[1:])
    if string[0] == '(' and string.find(')') != -1:
        date = datetime.strptime(string[1:11], '%d/%m/%Y')
        first_comma = string.find(',')
        second_comma = string.find(',', first_comma + 1)
        end_tuple = string.find(')', second_comma + 1)
        negative_delta = int(string[first_comma+1: second_comma])
        positive_delta = int(string[second_comma + 1: end_tuple])
        dates = [date]
        if negative_delta < 0:
            for delta in range(-1, negative_delta - 1, -1):
                dates += [date - timedelta(days=delta)]
        if positive_delta > 0:
            for delta in range(1, positive_delta + 1):
                dates += [date + timedelta(days=delta)]
        if string[end_tuple + 1] == ',':
            return dates + interpret_date(string[end_tuple + 2:])
        elif string[end_tuple + 1] == ']':
            return dates
        else:
            msg = '%r is not a valid date' % string
            argparse.ArgumentTypeError(msg)
    elif string.find(')') == -1:
        msg = '%r is not a valid date' % string
        argparse.ArgumentTypeError(msg)
    try:
        date = datetime.strptime(string[0:10], '%d/%m/%Y')
        if string[10] == ',':
            return [date] + interpret_date(string[11:])
        else:
            return [date]
    except ValueError:
        msg = '%r is not a valid date' % string
        argparse.ArgumentTypeError(msg)


def interpret_metro(string):
        pass
