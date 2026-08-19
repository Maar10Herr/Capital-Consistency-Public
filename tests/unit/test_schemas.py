import json
import unittest
from pathlib import Path

from capital_consistency.cashflows import discounted_economic_loss
from capital_consistency.schemas import EconomicHistory


PROJECT = Path(__file__).resolve().parents[2]


class SchemaTest(unittest.TestCase):
    def test_repeat_default_history(self):
        path = PROJECT / "examples" / "cashflow-histories" / "repeat-default.json"
        history = EconomicHistory.from_dict(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual([state.state for state in history.states].count("default"), 2)
        self.assertAlmostEqual(discounted_economic_loss(history), 5.65, places=12)


if __name__ == "__main__":
    unittest.main()
