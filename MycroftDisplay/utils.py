#!/usr/bin/env python

import re

class GridException(Exception): pass
class GridRectangleException(Exception):
    def __str__(self):
        return ("Supplied grid is not a rectangle")

class GridWrongSizeException(Exception):
    def __init__(self, img_code, total_bits_supplied, total_bits_required):
        self.img_code = img_code
        self.total_bits_supplied = total_bits_supplied
        self.total_bits_required = total_bits_required

    def __str__(self):
        return ("Img_code '%s' specifies %s pixels as height and width, but actually contains %s pixels" % (
            self.img_code, self.total_bits_required, self.total_bits_supplied))

class GridCharacterException(Exception):
    def __init__(self, remaining, fill, space):
        self.remaining = remaining
        self.fill = fill
        self.space = space

    def __str__(self):
        return ("Supplied grid contains characters (%s) other "
            "than the specified fill (%s) and space(%s)") % (self.remaining, self.fill, self.space)

def normalise_grid(grid):
    "removes all whitespace except newlines; remove blank lines"
    lines = [re.sub("\s", "", x) for x in grid.split("\n") if x.strip()]
    return "\n".join(lines)

def insert_grid(base, insert, x, y, fill="#", space="."):
    """Inserts the insert grid at position (x,y) into the base grid.
       Positions are 0-based. Result is normalised."""
    
    ins = [list(l) for l in normalise_grid(insert).split("\n")]
    nbas = [list(l) for l in normalise_grid(base).split("\n")]

    for iy in range(len(ins)):
        for ix in range(len(ins[iy])):
            if ins[iy][ix] == fill:
                base_x = x + ix
                base_y = y + iy
                nbas[base_y][base_x] = ins[iy][ix]

    return normalise_grid("\n".join(["".join(l) for l in nbas]))

