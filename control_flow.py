#!/usr/bin/python3

import argparse
import re

# Keep scope limited, don't do enums or typedefs or structs. Those may get complex.
declarators = ['float', 'long', 'double', 'int', 'char', 'short', 'byte', 'extern', 'volatile']
branchers = ['if', 'else', 'while', 'for', 'do']


def separate_statements(code):
    raw_statements = []
    for line in code:
        temp = line.split(';')
        try:
            temp.remove('\n')  # Remove 'empty' statements
            temp.remove('')
        except ValueError:
            next
        raw_statements = raw_statements + temp  # This should maintain order
    return raw_statements


def identify_blocks(code):
    pass


class Block(object):
    """docstring for Block"""
    def __init__(self, name):
        super(Block, self).__init__()
        self.name = name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Pass in a code snippet contained in a 
        text file, we identify the basic blocks 
        and create a pseudo control-flow graph''')
    parser.add_argument("textfile", help="The text file containing a code snippet.")
    args = parser.parse_args()
    if(not re.match(".+\.txt", args.textfile)):
        print("Please provide a .txt file!")
        exit(1)
    with open(args.textfile) as code:
        separate_statements(code)
    exit(0)