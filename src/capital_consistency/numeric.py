"""Shared rejection of non-finite or non-numeric scalar inputs."""

import math
from numbers import Real
from typing import Any


def require_finite(label: str, *values: Any) -> None:
    for value in values:
        try:
            valid = not isinstance(value, bool) and isinstance(value, Real) and math.isfinite(float(value))
        except (OverflowError, TypeError, ValueError):
            valid = False
        if not valid:
            raise ValueError("%s must contain only finite real numbers" % label)


def require_nonnegative_integer(label: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("%s must be a nonnegative integer" % label)
