"""Explicit episode partitioning; the independence window is an input, not hard-coded law."""

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .numeric import require_finite


@dataclass(frozen=True)
class DefaultInterval:
    start: float
    end: float

    def validate(self) -> None:
        require_finite("default interval", self.start, self.end)
        if self.start < 0 or self.end < self.start:
            raise ValueError("invalid default interval")


def merge_default_intervals(intervals: Iterable[DefaultInterval], independence_window: float) -> Tuple[DefaultInterval, ...]:
    """Merge ordered defaults separated by less than the stated independence window."""

    require_finite("independence window", independence_window)
    if independence_window < 0:
        raise ValueError("independence_window must be nonnegative")
    ordered = sorted(intervals, key=lambda item: (item.start, item.end))
    if not ordered:
        return ()
    for interval in ordered:
        interval.validate()
    merged: List[DefaultInterval] = [ordered[0]]
    for interval in ordered[1:]:
        previous = merged[-1]
        if interval.start < previous.end:
            raise ValueError("overlapping input intervals require prior semantic resolution")
        if interval.start - previous.end < independence_window:
            merged[-1] = DefaultInterval(previous.start, max(previous.end, interval.end))
        else:
            merged.append(interval)
    return tuple(merged)
