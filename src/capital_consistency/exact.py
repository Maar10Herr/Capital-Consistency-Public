"""Exact rational witnesses for allocation identities and floor failures."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ExactAllocation:
    drawn: Fraction
    undrawn: Fraction
    ccf: Fraction
    economic_loss: Fraction

    @property
    def ead(self) -> Fraction:
        return self.drawn + self.ccf * self.undrawn

    @property
    def lgd(self) -> Fraction:
        if self.ead <= 0:
            raise ValueError("EAD must be positive")
        return self.economic_loss / self.ead

    def identity_product(self) -> Fraction:
        return self.ead * self.lgd

    def floored_product(self, lgd_floor: Fraction) -> Fraction:
        return self.ead * max(self.lgd, lgd_floor)
