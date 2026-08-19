import unittest

from capital_consistency.optimization import (
    AllocationIntervalProblem,
    operational_loss_product,
    sharp_operational_product_bounds,
)


class EndpointReductionTest(unittest.TestCase):
    def test_endpoints_equal_finite_grid(self):
        cases = [
            AllocationIntervalProblem(100, 100, -0.5, 2.0, 10, 0.0, 1.0),
            AllocationIntervalProblem(100, 100, -0.5, 2.0, 10, 0.10, 1.0, 0.0),
            AllocationIntervalProblem(100, 100, -0.5, 2.0, 80, 0.10, 0.50),
        ]
        for problem in cases:
            exact = sharp_operational_product_bounds(problem)
            grid = []
            for step in range(251):
                q = problem.ccf_lower + step * (problem.ccf_upper - problem.ccf_lower) / 250
                ead = problem.ead_at(q)
                grid.append(
                    operational_loss_product(ead, problem.economic_loss, problem.lgd_floor, problem.lgd_upper_clip)
                )
            self.assertEqual(exact, (min(grid), max(grid)))

    def test_no_floor_or_clip_gives_singleton(self):
        problem = AllocationIntervalProblem(100, 100, 0, 1, 10)
        self.assertEqual(sharp_operational_product_bounds(problem), (10, 10))


if __name__ == "__main__":
    unittest.main()
