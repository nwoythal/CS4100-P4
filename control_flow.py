#!/usr/bin/python3

import argparse
import re
import pdb

# Keep scope limited, don't do enums or typedefs or structs. Those may get complex.
declarators = ['float', 'long', 'double', 'int', 'char', 'short', 'byte', 'extern', 'volatile']
branchers = ['if', 'else', 'while', 'for', 'do', '}']

block_prefix = "B" #Prefix for changing numerical block id's into proper ones.


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
    i = 0
    # pdb.set_trace()
    while(i < len(code) - 1):
        for branch in branchers:
            m = re.match("^" + branch, code[i])
            if(m):
                block_list = create_block(block_list, current_block, branch, current_block + 1) #Get new list with a new child block of current.
                current_block += 1 #Increment current block.
                if(branch == 'for'):
                    block_list[current_block].add_lines(code[i].lstrip())
                    i += 1
                    block_list[current_block].add_lines(code[i].lstrip())
                    i += 1
        block_list[current_block].add_lines(code[i].lstrip())
        i += 1
    return block_list

def to_dot_lang(block_list):
    """Outputs the list of blocks in the dot language (graphviz)"""
    result = ""
    for block in block_list:
        result += block_prefix + str(block.id) + str(block.lines) + "\n"
    for block in block_list:
        for child in block.children:
            result += block_prefix + str(block.id) + "->" + block_prefix + str(child.id) + "\n"
    return result

def create_block(block_list, current_block, _type, _id):
    """Creates a new block with the specified type and adds it to the list."""
    new_block = Block()
    new_block.set_id(_id)
    new_block.set_type(_type) 
    block_list[current_block].add_child(new_block) #Add the new block as a child of the current one
    block_list.append(new_block)
    return block_list

class Block(object):
    """A block object represents a control flow block."""

    def __init__(self):
        super(Block, self).__init__()
        self.lines = []
        self.variables = []
        self.children = []
        self.type = "normal"
        self.id = 0

    def add_lines(self, lines):
        self.lines.append(lines)

    def add_variables(self, var):
        self.variables.append(var)

    def add_child(self, child):
        self.children.append(child)

    def set_type(self, t):
        if((t not in branchers) and (t != "normal")):
            raise ValueError, "Block type must be in normal or " + str(branchers) + ", got " + t
        else:
            self.type = t

    def set_id(self, _id):
        self.id = _id;


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
    block_list = identify_blocks(line_by_line)
    print(to_dot_lang(block_list))
    exit(0)
    