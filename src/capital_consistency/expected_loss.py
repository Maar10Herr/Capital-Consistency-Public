"""Expected-loss functionals with explicit raw-versus-clipped semantics."""

from typing import Optional

from .decompositions import Allocation
from .numeric import require_finite


def expected_loss(
    allocation: Allocation,
    lgd_floor: float = 0.0,
    lgd_upper_clip: Optional[float] = None,
) -> float:
    """Return PD times EAD times LGD.

    The default is the raw loss-consistent LGD, with no implicit upper clip.
    Pass ``lgd_upper_clip`` to request an operational cap explicitly.
    """

    allocation.validate()
    require_finite("LGD floor", lgd_floor)
    if lgd_upper_clip is not None:
        require_finite("LGD upper clip", lgd_upper_clip)
    if lgd_floor < 0:
        raise ValueError("lgd_floor must be nonnegative")
    if lgd_upper_clip is None:
        lgd = max(lgd_floor, allocation.realised_lgd)
    else:
        lgd = allocation.operational_lgd(floor=lgd_floor, upper_clip=lgd_upper_clip)
    result = allocation.pd * allocation.ead * lgd
    require_finite("expected loss result", result)
    return result
