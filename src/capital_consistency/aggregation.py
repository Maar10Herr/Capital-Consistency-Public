"""Explicit aggregation operators; weights are part of the allocation rule."""

from typing import Iterable, Sequence

from .numeric import require_finite


def weighted_sum(values: Sequence[float], weights: Sequence[float]) -> float:
    require_finite("aggregation values", *values)
    require_finite("aggregation weights", *weights)
    if len(values) != len(weights) or any(weight < 0 for weight in weights):
        raise ValueError("invalid values or weights")
    result = sum(value * weight for value, weight in zip(values, weights))
    require_finite("weighted sum result", result)
    return result


def weighted_average(values: Sequence[float], weights: Sequence[float]) -> float:
    denominator = sum(weights)
    require_finite("weight total", denominator)
    if denominator <= 0:
        raise ValueError("weights must have positive total")
    result = weighted_sum(values, weights) / denominator
    require_finite("weighted average result", result)
    return result
