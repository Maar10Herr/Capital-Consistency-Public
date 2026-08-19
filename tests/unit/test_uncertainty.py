import math
import unittest
from copy import deepcopy

from capital_consistency.certificates import verify_certificate_data
from capital_consistency.joint_moc import independent_joint_coverage, minimum_scalar_uplift
from capital_consistency.uncertainty_sets import box_affine_upper, ellipsoid_affine_upper


class UncertaintyTest(unittest.TestCase):
    def test_spherical_support_beats_component_box(self):
        ellipsoid = ellipsoid_affine_upper([0, 0], [[1, 0], [0, 1]], [1, 1], 1)
        box = box_affine_upper([0, 0], [1, 1], [1, 1])
        self.assertTrue(math.isclose(ellipsoid, math.sqrt(2), rel_tol=1e-14))
        self.assertEqual(box, 2)
        self.assertLess(ellipsoid, box)

    def test_singular_covariance_supported(self):
        upper = ellipsoid_affine_upper([0, 0], [[1, 1], [1, 1]], [1, 1], 1)
        self.assertEqual(upper, 2.0)

    def test_non_psd_rejected(self):
        with self.assertRaises(ValueError):
            ellipsoid_affine_upper([0, 0], [[1, 2], [2, 1]], [1, 1], 1)
        with self.assertRaises(ValueError):
            ellipsoid_affine_upper([7], [[float("nan")]], [1], 1)
        with self.assertRaises(ValueError):
            ellipsoid_affine_upper([0], [[float("inf")]], [1], 1)
        with self.assertRaises(ValueError):
            ellipsoid_affine_upper(
                [0, 0],
                [[1e-300, 2e-300], [2e-300, 1e-300]],
                [1e150, 1e150],
                1,
            )
        with self.assertRaises(ValueError):
            ellipsoid_affine_upper(
                [0, 0],
                [[1e-300, 1e-299], [0.0, 1e-300]],
                [1e150, 1e150],
                1,
            )

    def test_extreme_scale_singular_covariance(self):
        upper = ellipsoid_affine_upper(
            [0, 0],
            [[1e308, 1e308], [1e308, 1e308]],
            [1e-154, 1e-154],
            1,
        )
        self.assertTrue(math.isclose(upper, 2.0, rel_tol=1e-14))

    def test_independent_ellipsoid_certificate_rejects_bad_witness(self):
        certificate = {
            "certificate_type": "ellipsoid_affine_support/v2",
            "center": [0.0, 0.0],
            "covariance": [[1.0, 0.0], [0.0, 1.0]],
            "gradient": [1.0, 1.0],
            "factor": [[1.0, 0.0], [0.0, 1.0]],
            "primal_z": [1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)],
            "radius": 1.0,
            "claimed_upper": math.sqrt(2.0),
        }
        self.assertTrue(verify_certificate_data(certificate))
        tampered = deepcopy(certificate)
        tampered["primal_z"] = [0.0, 0.0]
        self.assertFalse(verify_certificate_data(tampered))

    def test_marginal_95_not_joint_95(self):
        self.assertTrue(math.isclose(independent_joint_coverage(0.95, 2), 0.9025))

    def test_scalar_uplift(self):
        self.assertEqual(minimum_scalar_uplift(10, 12.5), 2.5)
        self.assertEqual(minimum_scalar_uplift(10, 9), 0)


if __name__ == "__main__":
    unittest.main()
