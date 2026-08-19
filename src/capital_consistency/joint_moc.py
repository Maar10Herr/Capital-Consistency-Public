"""Capital-scale joint-MoC primitives."""

from typing import Iterable

from .numeric import require_finite, require_nonnegative_integer


def minimum_scalar_uplift(baseline_risk: float, confidence_set_worst_risk: float) -> float:
    """Minimum risk-scale uplift when only scalar upper coverage is required."""

    require_finite("risk levels", baseline_risk, confidence_set_worst_risk)
    result = max(0.0, confidence_set_worst_risk - baseline_risk)
    require_finite("scalar uplift result", result)
    return result


def independent_joint_coverage(marginal_coverage: float, dimension: int) -> float:
    require_finite("marginal coverage", marginal_coverage)
    require_nonnegative_integer("dimension", dimension)
    if not 0 <= marginal_coverage <= 1 or dimension < 1:
        raise ValueError("invalid marginal coverage or dimension")
    return marginal_coverage ** dimension


def bonferroni_marginal_coverage(joint_coverage: float, dimension: int) -> float:
    require_finite("joint coverage", joint_coverage)
    require_nonnegative_integer("dimension", dimension)
    if not 0 <= joint_coverage <= 1 or dimension < 1:
        raise ValueError("invalid joint coverage or dimension")
    return 1.0 - (1.0 - joint_coverage) / dimension


def sidak_marginal_coverage(joint_coverage: float, dimension: int) -> float:
    require_finite("joint coverage", joint_coverage)
    require_nonnegative_integer("dimension", dimension)
    if not 0 <= joint_coverage <= 1 or dimension < 1:
        raise ValueError("invalid joint coverage or dimension")
    return joint_coverage ** (1.0 / dimension)


def simultaneous_upper_valid(component_events: Iterable[bool]) -> bool:
    return all(component_events)
