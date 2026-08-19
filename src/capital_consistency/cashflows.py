"""Economic loss from a fixed signed cash-flow convention."""

from .schemas import EconomicHistory
from .numeric import require_finite


OUTFLOW_KINDS = frozenset({"drawing", "recovery_cost", "write_off"})
INFLOW_KINDS = frozenset({"repayment", "recovery", "collateral_proceeds"})


def discounted_economic_loss(history: EconomicHistory) -> float:
    """Return discounted lender outflows minus inflows.

    This is an economic-history functional. A downstream allocation rule may
    repartition exposure and LGD but must not change this value.
    """

    history.validate()
    loss = 0.0
    for flow in history.cashflows:
        signed = flow.amount if flow.kind in OUTFLOW_KINDS else -flow.amount
        loss += signed * flow.discount_factor
        require_finite("discounted economic loss accumulation", loss)
    return loss
