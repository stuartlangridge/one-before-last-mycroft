import unittest

import Mark1
import utils

chars_to_img_code = {
    ":": "CIICAA",
    "0": "EIMHEEMHAA",
    "1": "EIIEMHAEAA",
    "2": "EIEHEFMFAA",
    "3": "EIEFEFMHAA",
    "4": "EIMBABMHAA",
    "5": "EIMFEFEHAA",
    "6": "EIMHEFEHAA",
    "7": "EIEAEAMHAA",
    "8": "EIMHEFMHAA",
    "9": "EIMBEBMHAA",
}

chars_to_grid = {
    "0": """   ....
               ....
               ###.
               #.#.
               #.#.
               #.#.
               ###.
               ....
        """,
    "1": """   ....
               ....
               .#..
               ##..
               .#..
               .#..
               ###.
               ....
    """,
    "2": """   ....
               ....
               ###.
               ..#.
               ###.
               #...
               ###.
               ....
    """,
    "3": """   ....
               ....
               ###.
               ..#.
               ###.
               ..#.
               ###.
               ....
    """,
    "4": """   ....
               ....
               #.#.
               #.#.
               ###.
               ..#.
               ..#.
               ....
    """,
    "5": """   ....
               ....
               ###.
               #...
               ###.
               ..#.
               ###.
               ....
    """,
    "6": """   ....
               ....
               ###.
               #...
               ###.
               #.#.
               ###.
               ....
    """,
    "7": """   ....
               ....
               ###.
               ..#.
               ..#.
               ..#.
               ..#.
               ....
    """,
    "8": """   ....
               ....
               ###.
               #.#.
               ###.
               #.#.
               ###.
               ....
    """,
    "9": """   ....
               ....
               ###.
               #.#.
               ###.
               ..#.
               ..#.
               ....
    """,
    ":": """   ..
               ..
               ..
               #.
               ..
               #.
               ..
               ..
    """
}

MYCROFT_GRID = utils.normalise_grid("""
     ................................
     #...##...#.##..####..##..###.###
     ##.##.#.#.#..#.#..#.#..#.#....#.
     #.#.#..#..#....###..#..#.###..#.
     #...#..#..#....#..#.#..#.#....#.
     #...#..#..#..#.#..#.#..#.#....#.
     #...#..#...##..#..#..##..#....#.
     ................................
""")

MYCROFT_IMG_CODE =  [
    ('QIOHEAIAEAOHCAEAIHEACAMDCECEECAAOH', 0, 0),
    ('QIKAKAGHAAMDCECEMDAAOHKAKAAACAOHCA', 16, 0)
]



class TestMark1Display(unittest.TestCase):
    def test_to_grid(self):
        for char in chars_to_img_code:
            img_code = chars_to_img_code[char]
            expected_grid = chars_to_grid[char]
            actual_grid = Mark1.to_grid(img_code, space=".", fill="#")
            expected_grid = utils.normalise_grid(expected_grid)
            actual_grid = utils.normalise_grid(actual_grid)
            self.assertEqual(expected_grid, actual_grid, "grids for %s did not match\nExpected:\n%s\n---Got:\n%s" % (char, expected_grid, actual_grid))

    def test_from_grid(self):
        for char in chars_to_img_code:
            expected_img_code = chars_to_img_code[char]
            grid = chars_to_grid[char]
            actual_img_code = Mark1.from_grid(grid, space=".", fill="#")
            self.assertEqual(expected_img_code, actual_img_code)

    def test_idempotent(self):
        for char in chars_to_img_code:
            start_img_code = chars_to_img_code[char]
            grid = Mark1.to_grid(start_img_code)
            finish_img_code = Mark1.from_grid(grid)
            self.assertEqual(start_img_code, finish_img_code)

    def test_bad_grid_chars(self):
        with self.assertRaises(utils.GridCharacterException):
            Mark1.from_grid("abcdef")

    def test_non_rectangle_grid(self):
        with self.assertRaises(utils.GridRectangleException):
            Mark1.from_grid("....\n...\n....\n")

    def test_too_big_grid(self):
        with self.assertRaises(utils.GridRectangleException):
            Mark1.from_grid("....\n...\n....\n")

    def test_from_large_grids(self):
        with self.assertRaises(Mark1.GridTooLargeException):
            Mark1.from_grid(MYCROFT_GRID)
        # ok, it fails, but from_large_grid should handle it
        self.assertEqual(Mark1.from_large_grid(MYCROFT_GRID),
            MYCROFT_IMG_CODE)

    def test_to_large_grids(self):
        actual = Mark1.to_large_grid(MYCROFT_IMG_CODE)
        self.assertEqual(actual, MYCROFT_GRID,
            "Expected return grid\n%s\nActual return grid\n%s\n" % (MYCROFT_GRID, actual))


class TestUtils(unittest.TestCase):
    def test_insert_grid(self):
        base = """
        ................
        ................
        ................
        ................
        ................
        ................
        ................
        ................
        """

        x = """
        #...#
        .#.#.
        ..#..
        .#.#.
        #...#
        """

        grid = utils.insert_grid(base, x, 1, 1)
        grid = utils.insert_grid(grid, x, 6, 3)
        grid = utils.insert_grid(grid, x, 10, 0)

        expected = utils.normalise_grid("""
        ..........#...#.
        .#...#.....#.#..
        ..#.#.......#...
        ...#..#...##.#..
        ..#.#..#.##...#.
        .#...#..#.......
        .......#.#......
        ......#...#.....
        """)

        self.assertEqual(len(grid), len(expected))
        self.assertEqual(grid, expected, "Expected return grid\n%s\nActual return grid\n%s\n" % (expected, grid))

if __name__ == '__main__':
    unittest.main()