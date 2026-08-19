import math
import unittest

from capital_consistency.irb import corporate_asset_correlation, corporate_capital_per_ead, corporate_rwa


class IrbTest(unittest.TestCase):
    def test_correlation_bounds(self):
        for pd in (1e-6, 0.001, 0.01, 0.1, 0.99):
            self.assertGreaterEqual(corporate_asset_correlation(pd), 0.12)
            self.assertLessEqual(corporate_asset_correlation(pd), 0.24)

    def test_linearity_in_lgd_and_ead(self):
        base = corporate_rwa(0.01, 0.2, 100.0)
        self.assertTrue(math.isclose(corporate_rwa(0.01, 0.4, 100.0), 2 * base, rel_tol=1e-14))
        self.assertTrue(math.isclose(corporate_rwa(0.01, 0.2, 200.0), 2 * base, rel_tol=1e-14))

    def test_zero_lgd_zero_capital(self):
        self.assertEqual(corporate_capital_per_ead(0.01, 0.0), 0.0)

    def test_invalid_units_caught(self):
        with self.assertRaises(ValueError):
            corporate_capital_per_ead(1.0, 0.45)
        with self.assertRaises(ValueError):
            corporate_capital_per_ead(0.01, 45.0)
        with self.assertRaises(ValueError):
            corporate_capital_per_ead(0.01, 0.45, 0.1)
        with self.assertRaises(ValueError):
            corporate_capital_per_ead(1e-6, 0.45)
        with self.assertRaises(ValueError):
            corporate_rwa(float("nan"), 0.45, 100.0)


if __name__ == "__main__":
    unittest.main()
