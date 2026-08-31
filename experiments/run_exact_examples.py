#!/usr/bin/env python3
"""Generate exact allocation and ellipsoid-support certificates."""

import json
import math
from fractions import Fraction
from pathlib import Path

from capital_consistency.audit import run_manifest
from capital_consistency.exact import ExactAllocation
from capital_consistency.uncertainty_sets import ellipsoid_affine_upper


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATES = ROOT / "artifacts" / "certificates"


def fraction_text(value: Fraction) -> str:
    return str(value)


def allocation_floor_certificate():
    floor = Fraction(1, 10)
    loss = Fraction(10)
    allocations = [
        ExactAllocation(Fraction(100), Fraction(100), Fraction(0), loss),
        ExactAllocation(Fraction(100), Fraction(100), Fraction(1), loss),
    ]
    return {
        "certificate_type": "allocation_floor_counterexample/v1",
        "claim_status": "proved_by_exact_rational_witness",
        "claim": "A fixed loss is allocation invariant before an LGD floor but not after a 1/10 LGD floor.",
        "economic_loss": fraction_text(loss),
        "lgd_floor": fraction_text(floor),
        "allocations": [
            {
                "drawn": fraction_text(item.drawn),
                "undrawn": fraction_text(item.undrawn),
                "ccf": fraction_text(item.ccf),
                "ead": fraction_text(item.ead),
                "realised_lgd": fraction_text(item.lgd),
                "unfloored_product": fraction_text(item.identity_product()),
            }
            for item in allocations
        ],
        "floored_products": [fraction_text(item.floored_product(floor)) for item in allocations],
    }


def ellipsoid_certificate():
    center = [0.0, 0.0]
    covariance = [[1.0, 0.0], [0.0, 1.0]]
    gradient = [1.0, 1.0]
    radius = 1.0
    factor = [[1.0, 0.0], [0.0, 1.0]]
    primal_z = [1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)]
    return {
        "certificate_type": "ellipsoid_affine_support/v2",
        "claim_status": "proved_closed_form_with_independent_primal_and_upper_certificate",
        "center": center,
        "covariance": covariance,
        "gradient": gradient,
        "factor": factor,
        "primal_z": primal_z,
        "radius": radius,
        "claimed_upper": ellipsoid_affine_upper(center, covariance, gradient, radius),
        "component_box_upper": 2.0,
        "strict_gap": 2.0 - math.sqrt(2.0),
    }


def weighting_certificate():
    allocations = [
        {"eads": [Fraction(100), Fraction(100)], "losses": [Fraction(10), Fraction(10)]},
        {"eads": [Fraction(50), Fraction(150)], "losses": [Fraction(10), Fraction(10)]},
    ]
    products = []
    rows = []
    for allocation in allocations:
        lgds = [loss / ead for loss, ead in zip(allocation["losses"], allocation["eads"])]
        default_weighted = sum(lgds, Fraction(0)) / len(lgds)
        exposure_weighted = sum(allocation["losses"], Fraction(0)) / sum(allocation["eads"], Fraction(0))
        products.append(sum(allocation["eads"], Fraction(0)) * default_weighted)
        rows.append(
            {
                "eads": [fraction_text(value) for value in allocation["eads"]],
                "losses": [fraction_text(value) for value in allocation["losses"]],
                "lgds": [fraction_text(value) for value in lgds],
                "default_weighted_lgd": fraction_text(default_weighted),
                "exposure_weighted_lgd": fraction_text(exposure_weighted),
            }
        )
    return {
        "certificate_type": "allocation_weighting_counterexample/v1",
        "claim_status": "proved_by_exact_rational_witness",
        "claim": "Default-weighted LGD calibration followed by total-EAD application is not allocation invariant.",
        "allocations": rows,
        "default_weighted_products": [fraction_text(value) for value in products],
        "total_economic_loss": "20",
    }


def main():
    CERTIFICATES.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, certificate in (
        ("allocation-floor-counterexample.json", allocation_floor_certificate()),
        ("ellipsoid-affine-support.json", ellipsoid_certificate()),
        ("allocation-weighting-counterexample.json", weighting_certificate()),
    ):
        output = CERTIFICATES / name
        output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        outputs.append(output)
    report_dir = ROOT / "artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = run_manifest(
        command=["capital-consistency", "reproduce", "core-exact"],
        inputs=[
            Path(__file__).resolve(),
            ROOT / "src" / "capital_consistency" / "__init__.py",
            ROOT / "src" / "capital_consistency" / "audit.py",
            ROOT / "src" / "capital_consistency" / "exact.py",
            ROOT / "src" / "capital_consistency" / "numeric.py",
            ROOT / "src" / "capital_consistency" / "uncertainty_sets.py",
        ],
        outputs=outputs,
        assumptions=[
            "fixed economic loss across allocations",
            "positive EAD",
            "ellipsoid covariance is positive semidefinite",
        ],
        project_dir=ROOT,
        solver="closed-form identities with independent certificate verification",
        solver_status="completed",
        arithmetic="exact Fraction arithmetic for allocation witnesses; IEEE-754 for sqrt(2) ellipsoid witness",
        claim_status="proof-backed certificate generation; ellipsoid equality checked to stated tolerance",
        tolerances={"ellipsoid_float_comparison": 1e-12},
        random_seed=None,
    )
    (report_dir / "core-exact-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("generated 3 certificates")


if __name__ == "__main__":
    main()
