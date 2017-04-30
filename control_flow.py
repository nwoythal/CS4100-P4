#!/usr/bin/python3

import argparse
import re
import pdb
import graphviz as gv

# Keep scope limited, don't do enums or typedefs or structs. Those may get complex.
declarators = ['float', 'long', 'double', 'int', 'char', 'short', 'byte', 'extern', 'volatile']
branchers = ['if', 'else', 'while', 'for', 'do', '}', '{']

block_prefix = "B"  # Prefix for changing numerical block id's into proper ones.
depth = 0


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
    global depth
    while(i < len(code)):
        for branch in branchers:
            m = re.match("^" + branch + r"\w*\(|^" + branch + r"$", code[i])
            if(m):
                block_list = create_block(block_list, current_block, branch, current_block + 1)  # Get new list with a new child block of current.
                current_block += 1  # Increment current block. 
                if(branch == 'for'):  # Because we split on ';', for loops will ALWAYS be broken into three lines.
                    block_list[current_block].add_lines(code[i].lstrip())
                    i += 1
                    block_list[current_block].add_lines(code[i].lstrip())
                    i += 1
                    block_list[current_block].add_lines(code[i].lstrip())
                    i += 1
                    block_list = create_block(block_list, current_block, 'normal', current_block + 1)
                    current_block += 1  # Increment current block. 
                    block_list[current_block].add_lines(code[i].lstrip())
                    break
                elif(branch == "}"):
                    depth -= 2  # Decrease scope by two to offset for the one we add later.
                    block_list[current_block].set_scope()
                if( not (re.search('{', code[i]) or re.search('{', code[i + 1])) and branch != '}'):
                    block_list[current_block].add_lines(code[i].lstrip())
                    depth += 1
                    block_list = create_block(block_list, current_block, branch, current_block + 1)
                    current_block += 1
                    i += 1
                    block_list[current_block].add_lines(code[i].lstrip())
                    depth -= 2
                    block_list = create_block(block_list, current_block, branch, current_block + 1)
                    current_block += 1
                    i += 1
                depth += 1
        if(code[i].lstrip() not in block_list[current_block].lines):                
            block_list[current_block].add_lines(code[i].lstrip())
        i += 1
    return block_list


def to_dot_lang(block_list):
    """Output the list of blocks in the dot language (graphviz)."""
    result = "digraph CFG {\n"
    for block in block_list:
        result += "\t" + block_prefix + str(block.id) + "[label=\"" + "; ".join(block.lines) + "\"]\n"
    for block in block_list:
        for child in block.children:
                result += "\t" + block_prefix + str(block.id) + "->" + block_prefix + str(child.id) + "\n"
    return result + "}"

def render_block_list(block_list, path):
    """Output the list of blocks in the dot language (graphviz)."""
    result = gv.Digraph(name="Control Flow Graph")
    for block in block_list:
        result.node(block_prefix + str(block.id), "; ".join(block.lines))
    for block in block_list:
        for child in block.children:
                result.edge(block_prefix + str(block.id), block_prefix + str(child.id))
    result.render(path, view=True)


def create_block(block_list, current_block, _type, _id):
    """Create a new block with the specified type and adds it to the list."""
    new_block = Block()
    new_block.set_id(_id)
    new_block.set_type(_type)
    new_block.set_scope()
    block_list[current_block].add_child(new_block)  # Add the new block as a child of the current one
    block_list.append(new_block)
    return block_list


class Block(object):
    """A block object represents a control flow block."""

    def __init__(self):
        super(Block, self).__init__()
        self.lines = []
        self.children = []
        self.type = "normal"
        self.id = 0
        self.scope = 0

    def add_lines(self, lines):
        self.lines.append(lines)

    def add_child(self, child):
        self.children.append(child)

    def set_type(self, t):
        if((t not in branchers) and (t != "normal")):
            raise ValueError("Block type must be in normal or " + str(branchers) + ", got " + t)
        else:
            self.type = t

    def set_id(self, _id):
        self.id = _id

    def set_scope(self):
        self.scope = depth

    def is_empty(self):
        return len(self.lines) == 0


def clean_blocks(block_list):
    """Remove lines only containing '}' or '{', and create branches pointing to correct children."""
    for block in block_list:
        line_count = len(block.lines)
        i = 0
        while i < line_count:
            block.lines[i] = block.lines[i].rstrip('{').rstrip('}').rstrip().rstrip('{')
            if not block.lines[i]:
                block.lines.remove(block.lines[i])
                line_count -= 1
            i += 1
    for block in block_list:
        if block.is_empty():
            block_list.remove(block)
    assign_children(block_list)

def assign_children(block_list):
    for i in range(len(block_list)):
        for child in block_list[i].children:
            # pdb.set_trace()
            if(child.is_empty()):
                block_list[i].children.extend(child.children)
                block_list[i].children.remove(child)
            if(block_list[i].type == "for" or block_list[i].type == "while" or block_list[i].type == "do"):
                child.children.append(block_list[i])
            if(block_list[i].type == "normal" and (child.type == "normal" or child.type == "}")):
                block_list[i].children.remove(child)
        if block_list[i].type in branchers:
            for j in range(i + 2, len(block_list)):
                if block_list[j].scope <= block_list[i].scope:
                    block_list[i].children.append(block_list[j])
                    break


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
    clean_blocks(block_list)
    s = to_dot_lang(block_list)
    print(s)
    try:
        render_block_list(block_list, 'test-output/render.gv')
    except RuntimeError:
        print("It looks like graphviz isn't installed on your system, or the path variable isn't configured correctly.")
    finally:
        exit(0)