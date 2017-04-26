#!/usr/bin/python3

import argparse
import re

# Keep scope limited, don't do enums or typedefs or structs. Those may get complex.
declarators = ['float', 'long', 'double', 'int', 'char', 'short', 'byte', 'extern', 'volatile']
branchers = ['if', 'else', 'while', 'for', 'do']

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
    for line in code:
        block_list[current_block].add_lines(line.lstrip())
        if(re.search("if", line)):
            
            #Template to be factored into new blocks of each type.
            block_list.append(Block())
            block_list[current_block].add_child(block_list[current_block+1]) #Add the new block as a child of the current one
            block_list[current_block+1].set_id(current_block+1)
            block_list[current_block+1].set_type("if") 
            current_block = current_block + 1

        elif(re.search("else", line)):
            
            block_list.append(Block())
            block_list[current_block].add_child(block_list[current_block+1]) #Add the new block as a child of the current one
            block_list[current_block+1].set_id(current_block+1)
            block_list[current_block+1].set_type("else") 
            current_block = current_block + 1

        elif(re.search("for", line)):
            
            block_list.append(Block())
            block_list[current_block].add_child(block_list[current_block+1]) #Add the new block as a child of the current one
            block_list[current_block+1].set_id(current_block+1)
            block_list[current_block+1].set_type("for") 
            current_block = current_block + 1

        elif(re.search("while", line)):
            
            block_list.append(Block())
            block_list[current_block].add_child(block_list[current_block+1]) #Add the new block as a child of the current one
            block_list[current_block+1].set_id(current_block+1)
            block_list[current_block+1].set_type("while") 
            current_block = current_block + 1

        elif(re.search("do", line)):
            
            block_list.append(Block())
            block_list[current_block].add_child(block_list[current_block+1]) #Add the new block as a child of the current one
            block_list[current_block+1].set_id(current_block+1)
            block_list[current_block+1].set_type("do") 
            current_block = current_block + 1

    print(current_block)
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
    