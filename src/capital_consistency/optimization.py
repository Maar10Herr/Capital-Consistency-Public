"""Closed-form allocation extrema for the one-facility floor/clipping model."""

from dataclasses import dataclass
from typing import Optional, Tuple

from .numeric import require_finite


@dataclass(frozen=True)
class AllocationIntervalProblem:
    drawn: float
    undrawn: float
    ccf_lower: float
    ccf_upper: float
    economic_loss: float
    lgd_floor: float = 0.0
    lgd_upper_clip: float = 1.0
    ccf_floor: Optional[float] = None

    def validate(self) -> None:
        require_finite(
            "allocation interval",
            self.drawn,
            self.undrawn,
            self.ccf_lower,
            self.ccf_upper,
            self.economic_loss,
            self.lgd_floor,
            self.lgd_upper_clip,
        )
        if self.ccf_floor is not None:
            require_finite("CCF floor", self.ccf_floor)
        if self.drawn < 0 or self.undrawn < 0 or self.ccf_lower > self.ccf_upper:
            raise ValueError("invalid exposure or CCF interval")
        if self.economic_loss < 0 or not 0 <= self.lgd_floor <= self.lgd_upper_clip:
            raise ValueError("invalid loss or LGD bounds")
        if self.ead_at(self.ccf_lower) <= 0:
            raise ValueError("the effective lower-endpoint EAD must be positive")
        require_finite("endpoint EAD", self.ead_at(self.ccf_lower), self.ead_at(self.ccf_upper))

    def effective_ccf(self, ccf: float) -> float:
        require_finite("CCF", ccf)
        return ccf if self.ccf_floor is None else max(ccf, self.ccf_floor)

    def ead_at(self, ccf: float) -> float:
        result = self.drawn + self.effective_ccf(ccf) * self.undrawn
        require_finite("computed EAD", result)
        return result


def operational_loss_product(ead: float, economic_loss: float, lgd_floor: float, lgd_upper_clip: float) -> float:
    """Return EAD times clipped/floored realised LGD without dividing.

    For positive EAD this equals min(u*EAD, max(f*EAD, L)).
    The expression is nondecreasing in EAD when 0 <= f <= u.
    """

    require_finite("operational-loss input", ead, economic_loss, lgd_floor, lgd_upper_clip)
    if ead <= 0 or economic_loss < 0 or not 0 <= lgd_floor <= lgd_upper_clip:
        raise ValueError("invalid operational-loss input")
    result = min(lgd_upper_clip * ead, max(lgd_floor * ead, economic_loss))
    require_finite("operational-loss result", result)
    return result


def sharp_operational_product_bounds(problem: AllocationIntervalProblem) -> Tuple[float, float]:
    """Sharp endpoint bounds; no grid or solver is required."""

    problem.validate()
    lower_ead = problem.ead_at(problem.ccf_lower)
    upper_ead = problem.ead_at(problem.ccf_upper)
    lower = operational_loss_product(
        lower_ead, problem.economic_loss, problem.lgd_floor, problem.lgd_upper_clip
    )
    upper = operational_loss_product(
        upper_ead, problem.economic_loss, problem.lgd_floor, problem.lgd_upper_clip
    )
    return lower, upper
