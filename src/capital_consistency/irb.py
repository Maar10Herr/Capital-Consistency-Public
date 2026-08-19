"""Basel-style corporate IRB formula used as a mathematical test functional.

The formula must be mapped to applicable EU exposure classes and legal versions
before regulatory conclusions are drawn. Inputs are decimals.
"""

import math
from statistics import NormalDist

from .numeric import require_finite


_NORMAL = NormalDist()


def corporate_asset_correlation(pd: float) -> float:
    require_finite("pd", pd)
    if not 0 < pd < 1:
        raise ValueError("pd must lie strictly between zero and one")
    weight = (1.0 - math.exp(-50.0 * pd)) / (1.0 - math.exp(-50.0))
    result = 0.12 * weight + 0.24 * (1.0 - weight)
    require_finite("asset correlation result", result)
    return result


def maturity_adjustment(pd: float, maturity: float) -> float:
    require_finite("pd and maturity", pd, maturity)
    if not 0 < pd < 1 or maturity <= 0:
        raise ValueError("invalid pd or maturity")
    if not 1.0 <= maturity <= 5.0:
        raise ValueError("this corporate test functional requires maturity in [1,5]")
    b = (0.11852 - 0.05478 * math.log(pd)) ** 2
    denominator = 1.0 - 1.5 * b
    if denominator <= 0:
        raise ValueError("maturity-adjustment denominator is nonpositive")
    numerator = 1.0 + (maturity - 2.5) * b
    if numerator < 0:
        raise ValueError("maturity-adjustment numerator is negative on this input domain")
    result = numerator / denominator
    require_finite("maturity adjustment result", result)
    return result


def corporate_capital_per_ead(pd: float, lgd: float, maturity: float = 2.5) -> float:
    """Corporate test kernel on its explicit numerically valid domain.

    PD must also yield a positive maturity-adjustment denominator; the routine
    does not silently substitute a regulatory PD floor.
    """

    require_finite("corporate capital inputs", pd, lgd, maturity)
    if not 0 <= lgd <= 1:
        raise ValueError("lgd must lie in [0,1]")
    correlation = corporate_asset_correlation(pd)
    conditional = (
        _NORMAL.inv_cdf(pd) / math.sqrt(1.0 - correlation)
        + math.sqrt(correlation / (1.0 - correlation)) * _NORMAL.inv_cdf(0.999)
    )
    unexpected = _NORMAL.cdf(conditional) - pd
    if unexpected < 0:
        raise ArithmeticError("unexpected-loss term became negative")
    result = lgd * unexpected * maturity_adjustment(pd, maturity)
    require_finite("capital-per-EAD result", result)
    return result


def corporate_rwa(pd: float, lgd: float, ead: float, maturity: float = 2.5) -> float:
    require_finite("corporate RWA inputs", pd, lgd, ead, maturity)
    if ead < 0:
        raise ValueError("ead must be nonnegative")
    result = 12.5 * ead * corporate_capital_per_ead(pd, lgd, maturity)
    require_finite("RWA result", result)
    return result
