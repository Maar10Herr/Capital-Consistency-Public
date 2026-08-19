"""Allocation of a fixed economic loss between EAD/CCF and LGD."""

from dataclasses import dataclass

from .numeric import require_finite


@dataclass(frozen=True)
class Allocation:
    drawn: float
    undrawn: float
    ccf: float
    economic_loss: float
    pd: float
    maturity: float = 2.5

    def validate(self) -> None:
        require_finite(
            "allocation", self.drawn, self.undrawn, self.ccf, self.economic_loss, self.pd, self.maturity
        )
        require_finite("computed EAD", self.ead)
        if self.drawn < 0 or self.undrawn < 0:
            raise ValueError("drawn and undrawn must be nonnegative")
        if self.ead <= 0:
            raise ValueError("EAD must be strictly positive")
        if self.economic_loss < 0:
            raise ValueError("economic_loss must be nonnegative")
        if not 0 < self.pd < 1:
            raise ValueError("pd must lie strictly between zero and one")

    @property
    def ead(self) -> float:
        return self.drawn + self.ccf * self.undrawn

    @property
    def realised_lgd(self) -> float:
        self.validate()
        result = self.economic_loss / self.ead
        require_finite("realised LGD", result)
        return result

    def operational_lgd(self, floor: float = 0.0, lower_clip: float = 0.0, upper_clip: float = 1.0) -> float:
        require_finite("LGD operators", floor, lower_clip, upper_clip)
        if not 0 <= lower_clip <= upper_clip:
            raise ValueError("invalid clipping interval")
        if floor < 0:
            raise ValueError("floor must be nonnegative")
        if floor > upper_clip:
            raise ValueError("floor cannot exceed upper clip")
        return min(upper_clip, max(lower_clip, floor, self.realised_lgd))


def allocation_identity(allocation: Allocation) -> float:
    """Exactly economic_loss in real arithmetic, up to floating arithmetic."""

    result = allocation.ead * allocation.realised_lgd
    require_finite("allocation identity", result)
    return result
