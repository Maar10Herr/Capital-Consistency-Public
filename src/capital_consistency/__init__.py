"""Capital-consistency research code. Public APIs use decimals, not percentages."""

from .decompositions import Allocation
from .irb import corporate_capital_per_ead, corporate_rwa

__all__ = ["Allocation", "corporate_capital_per_ead", "corporate_rwa"]
__version__ = "0.2.0"
