import json
import unittest
from copy import deepcopy
from pathlib import Path

from capital_consistency.certificates import verify_certificate, verify_certificate_data


ROOT = Path(__file__).resolve().parents[2]


def load_certificate(name):
    with (ROOT / "artifacts" / "certificates" / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class CertificateSemanticsTest(unittest.TestCase):
    def test_floor_certificate_rejects_negative_exposure_component(self):
        certificate = load_certificate("allocation-floor-counterexample.json")
        forged = deepcopy(certificate)
        forged["allocations"][0]["drawn"] = "-100"
        forged["allocations"][0]["ccf"] = "2"
        self.assertFalse(verify_certificate_data(forged))

    def test_weighting_certificate_requires_same_declared_economic_loss(self):
        certificate = load_certificate("allocation-weighting-counterexample.json")
        forged = deepcopy(certificate)
        second = forged["allocations"][1]
        second["losses"] = ["11", "10"]
        second["lgds"] = ["11/50", "1/15"]
        second["default_weighted_lgd"] = "43/300"
        second["exposure_weighted_lgd"] = "21/200"
        forged["default_weighted_products"][1] = "86/3"
        self.assertFalse(verify_certificate_data(forged))

    def test_unknown_certificate_type_is_invalid(self):
        self.assertFalse(verify_certificate_data({"certificate_type": "unknown/v1"}))

    def test_malformed_certificate_file_is_controlled_invalid(self):
        self.assertFalse(verify_certificate(ROOT / "tests" / "fixtures" / "malformed-certificate.json"))


if __name__ == "__main__":
    unittest.main()
