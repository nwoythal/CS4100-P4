#!/usr/bin/python3

import argparse
import re

# Keep scope limited, don't do enums or typedefs or structs. Those may get complex.
declarators = ['float', 'long', 'double', 'int', 'char', 'short', 'byte', 'extern', 'volatile']
branchers = ['if', 'else', 'while', 'for', 'do']


def separate_statements(code):
    raw_statements = []
    for line in code:
        temp = line.rstrip()
        temp = temp.split(';')
        for elem in temp:
            elem = elem.lstrip()
            if(not elem == ''):
                raw_statements.append(elem)
    return raw_statements


def identify_blocks(code):
    block_list = []
    current_block = 0
    block_list.append(Block())
    for line in code:
        block_list[current_block].add_lines(line.lstrip())
        if(re.search("if", line)):
            block_list.append(Block())
            current_block = current_block + 1
        elif(re.search("else", line)):
            block_list.append(Block())
            current_block = current_block + 1
        elif(re.search("for", line)):
            block_list.append(Block())
            current_block = current_block + 1
        elif(re.search("while", line)):
            block_list.append(Block())
            current_block = current_block + 1
        elif(re.search("do", line)):
            block_list.append(Block())
            current_block = current_block + 1
    print(current_block)


class Block(object):
    """A block object represents a control flow block."""

    def __init__(self):
        super(Block, self).__init__()
        self.lines = []
        self.variables = []

    def add_lines(self, lines):
        self.lines.append(lines)

    def add_variables(self, var):
        self.varaibles.append(var)


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
        line_by_line = separate_statements(code)
    identify_blocks(line_by_line)
    exit(0)