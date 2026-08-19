import unittest

from capital_consistency.irb import corporate_capital_per_ead


class PdNonmonotonicityTest(unittest.TestCase):
    def test_componentwise_upper_pd_can_lower_unexpected_capital(self):
        at_thirty_percent = corporate_capital_per_ead(0.30, 0.45)
        at_ninety_percent = corporate_capital_per_ead(0.90, 0.45)
        self.assertGreater(at_thirty_percent, at_ninety_percent)

    def test_capital_tends_toward_zero_near_default_certainty(self):
        self.assertGreater(
            corporate_capital_per_ead(0.99, 0.45),
            corporate_capital_per_ead(0.999, 0.45),
        )


if __name__ == "__main__":
    unittest.main()
