"""Independent slow implementation used only to cross-check the central IRB formula."""

import math

from .numeric import require_finite


def normal_cdf(value: float) -> float:
    require_finite("normal variate", value)
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def normal_inverse(probability: float) -> float:
    require_finite("probability", probability)
    if not 0 < probability < 1:
        raise ValueError("probability must lie strictly between zero and one")
    lower, upper = -10.0, 10.0
    for _ in range(200):
        midpoint = (lower + upper) / 2.0
        if normal_cdf(midpoint) < probability:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def corporate_capital_per_ead_reference(pd: float, lgd: float, maturity: float) -> float:
    require_finite("reference IRB inputs", pd, lgd, maturity)
    if not 0 < pd < 1 or not 0 <= lgd <= 1 or not 1 <= maturity <= 5:
        raise ValueError("invalid reference IRB inputs")
    exponential_ratio = (1.0 - math.exp(-50.0 * pd)) / (1.0 - math.exp(-50.0))
    correlation = 0.12 * exponential_ratio + 0.24 * (1.0 - exponential_ratio)
    conditional = normal_inverse(pd) / math.sqrt(1.0 - correlation)
    conditional += math.sqrt(correlation / (1.0 - correlation)) * normal_inverse(0.999)
    b = (0.11852 - 0.05478 * math.log(pd)) ** 2
    denominator = 1.0 - 1.5 * b
    if denominator <= 0:
        raise ValueError("reference maturity adjustment is outside its valid domain")
    maturity_factor = (1.0 + (maturity - 2.5) * b) / denominator
    if maturity_factor < 0:
        raise ValueError("reference maturity adjustment is outside its valid domain")
    return lgd * (normal_cdf(conditional) - pd) * maturity_factor
