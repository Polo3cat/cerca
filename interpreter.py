import argparse
import ast


def interpret_key(string):
    interpretation = ast.literal_eval(string)
    if isinstance(interpretation, str) or isinstance(interpretation, tuple) or isinstance(interpretation, list):
        print('OK')
        return interpretation
    msg = '%r is not a valid key' % string
    argparse.ArgumentTypeError(msg)


def interpret_date(string):
        pass


def interpret_metro(string):
        pass
