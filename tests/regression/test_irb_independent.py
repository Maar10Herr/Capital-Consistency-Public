import math
import random
import unittest

from capital_consistency.irb import corporate_capital_per_ead
from capital_consistency.irb_reference import corporate_capital_per_ead_reference


class IndependentIrbTest(unittest.TestCase):
    def test_independent_erf_bisection_implementation(self):
        rng = random.Random(20260806)
        for _ in range(100):
            pd = rng.uniform(0.0001, 0.999)
            lgd = rng.uniform(0.0, 1.0)
            maturity = rng.uniform(1.0, 5.0)
            main = corporate_capital_per_ead(pd, lgd, maturity)
            reference = corporate_capital_per_ead_reference(pd, lgd, maturity)
            self.assertTrue(math.isclose(main, reference, rel_tol=5e-13, abs_tol=5e-13))


if __name__ == "__main__":
    unittest.main()
