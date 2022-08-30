# encoding: utf-8

'''Tests the library functions.
'''

import unittest

from ckanext.report import lib


PERCENTAGES = [
    {'input': (2, 4), 'expected': 50},
    {'input': (10, 100), 'expected': 10},
    {'input': (1, 3), 'expected': 33},
    {'input': (7, 0), 'expected': 100}
]


class TestLibrary(unittest.TestCase):

    def test_percent(self):
        """ Test the conversion from fraction to percentage.
        """
        for case in PERCENTAGES:
            print("Testing percentage for {} / {}".format(case['input'][0], case['input'][1]))
            self.assertEqual(lib.percent(case['input'][0], case['input'][1]), case['expected'])


if __name__ == '__main__':
    unittest.main()
