import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from capital_consistency.cli import cmd_evaluate_allocation


class CliDomainTest(unittest.TestCase):
    def test_raw_lgd_outside_rwa_domain_returns_status(self):
        args = SimpleNamespace(
            file="examples/mathematical-edge-cases/raw-lgd-over-one.json",
            lgd_floor=0.0,
            lgd_upper_clip=None,
        )
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cmd_evaluate_allocation(args), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["expected_loss"], 0.02)
        self.assertIsNone(result["rwa"])
        self.assertIn("outside corporate test domain", result["rwa_status"])


if __name__ == "__main__":
    unittest.main()
