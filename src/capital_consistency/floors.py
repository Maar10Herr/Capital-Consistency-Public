"""Transparent scalar floor and clipping operators."""

from .numeric import require_finite


def floor_value(value: float, floor: float) -> float:
    require_finite("floor inputs", value, floor)
    return max(value, floor)


def clip_value(value: float, lower: float, upper: float) -> float:
    require_finite("clip inputs", value, lower, upper)
    if lower > upper:
        raise ValueError("lower exceeds upper")
    return min(upper, max(lower, value))
