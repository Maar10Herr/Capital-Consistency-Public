import unittest
from fractions import Fraction

from capital_consistency.aggregation import weighted_average


class WeightingCounterexampleTest(unittest.TestCase):
    def test_default_weighted_then_apply_is_not_invariant(self):
        losses = [Fraction(10), Fraction(10)]
        eads_a = [Fraction(100), Fraction(100)]
        eads_b = [Fraction(50), Fraction(150)]
        lgds_a = [loss / ead for loss, ead in zip(losses, eads_a)]
        lgds_b = [loss / ead for loss, ead in zip(losses, eads_b)]
        product_a = sum(eads_a) * weighted_average(lgds_a, [1, 1])
        product_b = sum(eads_b) * weighted_average(lgds_b, [1, 1])
        self.assertEqual(product_a, Fraction(20))
        self.assertEqual(product_b, Fraction(80, 3))

    def test_exposure_weighting_preserves_total_loss(self):
        losses = [Fraction(10), Fraction(10)]
        for eads in ([Fraction(100), Fraction(100)], [Fraction(50), Fraction(150)]):
            lgds = [loss / ead for loss, ead in zip(losses, eads)]
            product = sum(eads) * weighted_average(lgds, eads)
            self.assertEqual(product, sum(losses))


if __name__ == "__main__":
    unittest.main()
