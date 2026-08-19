import math
import unittest

from capital_consistency.decompositions import Allocation, allocation_identity
from capital_consistency.expected_loss import expected_loss
from capital_consistency.irb import corporate_rwa


class AllocationIdentityTest(unittest.TestCase):
    def setUp(self):
        self.low = Allocation(100.0, 100.0, 0.0, 10.0, 0.01)
        self.high = Allocation(100.0, 100.0, 1.0, 10.0, 0.01)

    def test_loss_identity(self):
        self.assertEqual(allocation_identity(self.low), 10.0)
        self.assertEqual(allocation_identity(self.high), 10.0)

    def test_expected_loss_invariant_without_floor(self):
        self.assertEqual(expected_loss(self.low), expected_loss(self.high))

    def test_rwa_invariant_without_floor(self):
        first = corporate_rwa(self.low.pd, self.low.realised_lgd, self.low.ead, self.low.maturity)
        second = corporate_rwa(self.high.pd, self.high.realised_lgd, self.high.ead, self.high.maturity)
        self.assertTrue(math.isclose(first, second, rel_tol=1e-14))

    def test_lgd_floor_breaks_invariance(self):
        self.assertEqual(expected_loss(self.low, 0.10), 0.1)
        self.assertEqual(expected_loss(self.high, 0.10), 0.2)

    def test_raw_expected_loss_does_not_silently_upper_clip(self):
        low_ead = Allocation(1.0, 1.0, 0.0, 2.0, 0.01)
        high_ead = Allocation(1.0, 1.0, 1.0, 2.0, 0.01)
        self.assertEqual(expected_loss(low_ead), 0.02)
        self.assertEqual(expected_loss(high_ead), 0.02)
        self.assertEqual(expected_loss(low_ead, lgd_upper_clip=1.0), 0.01)
        self.assertEqual(expected_loss(high_ead, lgd_upper_clip=1.0), 0.02)

    def test_floor_above_upper_clip_rejected(self):
        with self.assertRaises(ValueError):
            self.low.operational_lgd(floor=1.1, upper_clip=1.0)

    def test_negative_ccf_allowed_if_ead_positive(self):
        allocation = Allocation(100.0, 100.0, -0.5, 10.0, 0.01)
        allocation.validate()
        self.assertEqual(allocation.ead, 50.0)

    def test_nonpositive_ead_rejected(self):
        with self.assertRaises(ValueError):
            Allocation(100.0, 100.0, -1.0, 10.0, 0.01).validate()

    def test_nonfinite_allocation_rejected(self):
        with self.assertRaises(ValueError):
            Allocation(float("nan"), 0.0, 0.0, 0.0, 0.01).validate()
        with self.assertRaises(ValueError):
            Allocation(1.0, 1.0, float("inf"), 1.0, 0.01).validate()
        with self.assertRaises(ValueError):
            Allocation(1.0, 1e308, 1e308, 1.0, 0.01).validate()
        with self.assertRaises(ValueError):
            _ = Allocation(5e-324, 0.0, 0.0, 1e308, 0.01).realised_lgd


if __name__ == "__main__":
    unittest.main()
