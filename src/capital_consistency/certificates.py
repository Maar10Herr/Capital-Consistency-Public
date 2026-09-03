"""Machine-readable certificates with a deliberately independent verifier."""

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict


def _fraction(text: str) -> Fraction:
    return Fraction(text)


def verify_allocation_floor(certificate: Dict[str, Any]) -> bool:
    floor = _fraction(certificate["lgd_floor"])
    economic_loss = _fraction(certificate["economic_loss"])
    if floor < 0 or economic_loss < 0:
        return False
    products = []
    for row in certificate["allocations"]:
        drawn = _fraction(row["drawn"])
        undrawn = _fraction(row["undrawn"])
        ccf = _fraction(row["ccf"])
        if drawn < 0 or undrawn < 0:
            return False
        ead = drawn + ccf * undrawn
        if ead <= 0:
            return False
        lgd = economic_loss / ead
        if _fraction(row["ead"]) != ead or _fraction(row["realised_lgd"]) != lgd:
            return False
        if _fraction(row["unfloored_product"]) != economic_loss:
            return False
        products.append(ead * max(lgd, floor))
    claimed = [_fraction(value) for value in certificate["floored_products"]]
    return products == claimed and len(set(products)) > 1


def verify_ellipsoid_support(certificate: Dict[str, Any]) -> bool:
    """Verify a primal witness and Cauchy upper bound independently.

    The verifier deliberately does not call the production support function.
    A supplied factor B proves covariance = B B^T and represents the set as
    center + B z with ||z|| <= radius.
    """

    center = [float(value) for value in certificate["center"]]
    covariance = [[float(value) for value in row] for row in certificate["covariance"]]
    gradient = [float(value) for value in certificate["gradient"]]
    factor = [[float(value) for value in row] for row in certificate["factor"]]
    primal_z = [float(value) for value in certificate["primal_z"]]
    radius = float(certificate["radius"])
    claimed = float(certificate["claimed_upper"])
    n = len(center)
    if n == 0 or len(gradient) != n or len(covariance) != n or len(factor) != n or radius < 0:
        return False
    if any(len(row) != n for row in covariance):
        return False
    factor_width = len(factor[0]) if factor else 0
    if factor_width == 0 or any(len(row) != factor_width for row in factor) or len(primal_z) != factor_width:
        return False
    if not all(
        math.isfinite(value)
        for value in (
            center
            + gradient
            + primal_z
            + [radius, claimed]
            + [item for row in covariance for item in row]
            + [item for row in factor for item in row]
        )
    ):
        return False

    reconstructed = [
        [sum(factor[i][k] * factor[j][k] for k in range(factor_width)) for j in range(n)]
        for i in range(n)
    ]
    if any(
        not math.isclose(covariance[i][j], reconstructed[i][j], rel_tol=1e-12, abs_tol=1e-12)
        for i in range(n)
        for j in range(n)
    ):
        return False

    primal_norm = math.sqrt(sum(value * value for value in primal_z))
    if primal_norm > radius + 1e-12:
        return False
    primal_theta = [
        center[i] + sum(factor[i][k] * primal_z[k] for k in range(factor_width))
        for i in range(n)
    ]
    primal_value = sum(a * theta for a, theta in zip(gradient, primal_theta))

    transposed_action = [
        sum(factor[i][k] * gradient[i] for i in range(n)) for k in range(factor_width)
    ]
    cauchy_upper = sum(a * mu for a, mu in zip(gradient, center)) + radius * math.sqrt(
        sum(value * value for value in transposed_action)
    )
    return math.isclose(primal_value, claimed, rel_tol=1e-12, abs_tol=1e-12) and math.isclose(
        cauchy_upper, claimed, rel_tol=1e-12, abs_tol=1e-12
    )


def verify_weighting_counterexample(certificate: Dict[str, Any]) -> bool:
    products = []
    allocation_total_losses = []
    for allocation in certificate["allocations"]:
        eads = [_fraction(value) for value in allocation["eads"]]
        losses = [_fraction(value) for value in allocation["losses"]]
        if not eads or len(eads) != len(losses) or any(ead <= 0 for ead in eads) or any(loss < 0 for loss in losses):
            return False
        lgds = [loss / ead for loss, ead in zip(losses, eads)]
        default_weighted_lgd = sum(lgds, Fraction(0)) / len(lgds)
        exposure_weighted_lgd = sum(losses, Fraction(0)) / sum(eads, Fraction(0))
        if [_fraction(value) for value in allocation["lgds"]] != lgds:
            return False
        if _fraction(allocation["default_weighted_lgd"]) != default_weighted_lgd:
            return False
        if _fraction(allocation["exposure_weighted_lgd"]) != exposure_weighted_lgd:
            return False
        total_loss = sum(losses, Fraction(0))
        allocation_total_losses.append(total_loss)
        products.append(sum(eads, Fraction(0)) * default_weighted_lgd)
    claimed = [_fraction(value) for value in certificate["default_weighted_products"]]
    declared_total = _fraction(certificate["total_economic_loss"])
    return (
        products == claimed
        and len(set(products)) > 1
        and len(set(allocation_total_losses)) == 1
        and allocation_total_losses[0] == declared_total
    )


def verify_certificate_data(certificate: Dict[str, Any]) -> bool:
    try:
        if not isinstance(certificate, dict):
            return False
        certificate_type = certificate.get("certificate_type")
        if certificate_type == "allocation_floor_counterexample/v1":
            return verify_allocation_floor(certificate)
        if certificate_type == "ellipsoid_affine_support/v2":
            return verify_ellipsoid_support(certificate)
        if certificate_type == "allocation_weighting_counterexample/v1":
            return verify_weighting_counterexample(certificate)
        return False
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False


def verify_certificate(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return verify_certificate_data(json.load(handle))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return False
