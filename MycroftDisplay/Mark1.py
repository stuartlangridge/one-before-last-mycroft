#!/usr/bin/python
"""
Convert a pixel-art version of the Mark 1's display into the code needed to display it, and back again.

Stuart Langridge <sil@kryogenix.org>, March 2018

The display is 32x8. Encoding this into an img_code is done by breaking it into groups of 4 vertical bits,
least-significant-bit first, and then making that binary bit value into a letter from A (0) onwards, thus:
A 0000
B 1000
C 0100
D 1100
E 0010
F 1010
G 0110
H 1110
I 0001
J 1001
K 0101
L 1101
M 0011
N 1011
O 0111
P 1111

(that is: each is binary, but in reverse order)

So you can do:

img_code = Mark1.from_grid('''
................
................
#...#....#..###.
##.##...#.#..#..
#.#.#...###..#..
#...#...#.#..#..
#...#.#.#.#.###.
................
''')

and get back "QIMHIAABIAMHAAAEAAIHEBIHAAEEMHEEAA"

"""

import utils

class GridTooLargeException(utils.GridException):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def __str__(self): return "Grid of size %sx%s is larger than the Mark 1 maximum size of 16x8" % (self.width, self.height)

def _img_code_to_numbers(img_code):
    vals = [ord(x) - 65 for x in img_code]
    width = vals[0]
    height = vals[1]
    pixels = vals[2:]

    if width > 16 or height > 8:
        raise GridTooLargeException(width, height)

    total_bits_required = width * height
    total_bits_supplied = len(pixels) * 4

    if total_bits_supplied != total_bits_required:
        raise utils.GridWrongSizeException(img_code, total_bits_supplied, total_bits_required)

    return width, height, pixels

def to_grid(img_code, space=".", fill="#"):
    "Convert an img_code for the Mycroft display into a pixel art rendition of the display"
    # convert each letter to a number
    width, height, pixels = _img_code_to_numbers(img_code)

    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(".")
        grid.append(row)

    # each pixels entry is four bits, starting from top left and then going down, then across
    xp = 0
    yp = 0
    for p in pixels:
        for i in range(4):
            bit_set = p & pow(2, i)
            if bit_set:
                grid[yp][xp] = fill
            else:
                grid[yp][xp] = space
            yp += 1
            if yp == height:
                yp = 0
                xp += 1

    grid = "\n".join(["".join(x) for x in grid])
    return grid

def _confirm_grid_ok(g, space, fill):
    # note: this does not check for size, so that large grids can use it too
    # confirm there aren't any other characters
    remaining = g.replace(space, "").replace(fill, "").replace("\n", "")
    if len(remaining) > 0:
        remaining = "".join(sorted(list(set(remaining))))
        raise utils.GridCharacterException(remaining, fill, space)

    # confirm that all rows are the same length
    lines = g.split("\n")
    height = len(lines)
    if len(lines) == 0: return ""
    width = len(lines[0])
    matching = [len(x) == width for x in lines]
    if not all(matching):
        raise utils.GridRectangleException
    return width, height

def from_grid(grid, space=".", fill="#"):
    "Convert a pixel art rendition of the display into an img_code to be given to enclosure.mouth_display()"
    g = utils.normalise_grid(grid)
    width, height = _confirm_grid_ok(g, space, fill)

    # Since this is the Mark 1, the grid can't be larger than 16x8
    if width > 16 or height > 8:
        raise GridTooLargeException(width, height)

    lines = g.split("\n")
    # now walk through the grid
    xp = 0
    yp = 0
    accum = []
    letters = []
    while xp < width and yp < height:
        accum.append(lines[yp][xp])
        yp += 1
        if yp == height:
            yp = 0
            xp += 1
        if len(accum) == 4:
            value = 0
            for i in range(len(accum)):
                if accum[i] == fill:
                    value += pow(2, i)
            letter = chr(65 + value)
            letters.append(letter)
            accum = []
    img_code = "%s%s%s" % (chr(65 + width), chr(65 + height), "".join(letters))
    return img_code

def from_large_grid(grid, space=".", fill="#"):
    """Handles grids larger than the Mark 1's 16x8, by breaking them up into blocks.
       Returns a list of (img_code, x, y) tuples.
    """
    g = utils.normalise_grid(grid)
    width, height = _confirm_grid_ok(g, space, fill)

    if width <= 16 and height <= 8:
        # this is not actually a large grid. Defer to from_grid.
        return [(from_grid(grid, space, fill), 0, 0),]

    result = []
    lines = g.split("\n")
    for x in range(0, width, 16):
        for y in range(0, height, 8):
            this_grid = []
            for yy in range(y, min(height, y+8)):
                this_grid.append(lines[yy][x:x+16])
            this_grid = "\n".join(this_grid)
            result.append((from_grid(this_grid, space, fill), x, y))
    return result


def to_large_grid(img_code_list, space=".", fill="#"):
    """Handles a list of (img_code, x, y) tuples as returned by from_large_grid.
       Returns one large grid.
    """
    # get overall size of grid
    max_x = 0
    max_y = 0
    for img_code, x, y in img_code_list:
        width, height, pixels = _img_code_to_numbers(img_code)
        this_max_x = x + width
        if this_max_x > max_x: max_x = this_max_x
        this_max_y = y + height
        if this_max_y > max_y: max_y = this_max_y

    # make a whole grid which is that big
    whole = "\n".join(["." * max_x for y in range(max_y)])

    # make a grid from each img_code and composite it into the larger grid
    for img_code, x, y in img_code_list:
        subgrid = to_grid(img_code)
        whole = utils.insert_grid(whole, subgrid, x, y)

    return whole

to_img_code = from_grid
from_img_code = to_grid