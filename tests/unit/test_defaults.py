import unittest

from capital_consistency.defaults import DefaultInterval, merge_default_intervals


class DefaultEpisodeTest(unittest.TestCase):
    def test_independence_window_changes_partition(self):
        intervals = [DefaultInterval(0.0, 1.0), DefaultInterval(1.5, 2.0), DefaultInterval(3.0, 4.0)]
        self.assertEqual(len(merge_default_intervals(intervals, 0.4)), 3)
        self.assertEqual(merge_default_intervals(intervals, 0.75), (DefaultInterval(0.0, 2.0), DefaultInterval(3.0, 4.0)))

    def test_overlaps_rejected(self):
        with self.assertRaises(ValueError):
            merge_default_intervals([DefaultInterval(0, 2), DefaultInterval(1, 3)], 0.5)


if __name__ == "__main__":
    unittest.main()
