import random

__author__ = 'enrico'

import unittest
import isle

class TestAngle(unittest.TestCase):
    def setUp(self):
        self.x = random.randint(0, sum(self.genes)-1)
        self.genes = [random.randint(1, 9) for i in xrange(8)]
        random.shuffle(self.genes)

    def test_something(self):
        self.assertEqual(
            isle.angle(self.genes, 0, self.x),
            isle.angle2(self.genes, self.x)
        )

if __name__ == '__main__':
    unittest.main()
