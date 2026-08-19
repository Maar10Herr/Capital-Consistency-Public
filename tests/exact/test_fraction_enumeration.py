import unittest
from fractions import Fraction

from capital_consistency.exact import ExactAllocation


class ExactEnumerationTest(unittest.TestCase):
    def test_all_small_positive_ead_cases(self):
        tested = 0
        for drawn in range(0, 4):
            for undrawn in range(0, 4):
                for ccf in (Fraction(-1), Fraction(0), Fraction(1, 2), Fraction(1), Fraction(2)):
                    allocation = ExactAllocation(Fraction(drawn), Fraction(undrawn), ccf, Fraction(1, 3))
                    if allocation.ead > 0:
                        self.assertEqual(allocation.identity_product(), Fraction(1, 3))
                        tested += 1
        self.assertEqual(tested, 63)


if __name__ == "__main__":
    unittest.main()
