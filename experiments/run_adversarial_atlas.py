#!/usr/bin/env python3
"""Deterministic adversarial atlas; evidence is finite-set verification only."""

import json
import math
import random
from pathlib import Path

from capital_consistency.audit import run_manifest
from capital_consistency.decompositions import Allocation
from capital_consistency.irb import corporate_capital_per_ead, corporate_rwa


ROOT = Path(__file__).resolve().parents[1]
SEED = 20260806
CASES = 5000


def main():
    rng = random.Random(SEED)
    raw_failures = []
    floor_breaks = 0
    maximum_raw_error = 0.0
    for case_id in range(CASES):
        drawn = rng.uniform(1.0, 1000.0)
        undrawn = rng.uniform(0.0, 1000.0)
        lower_ccf_boundary = -drawn / undrawn if undrawn > 0 else -1.0
        q1 = rng.uniform(max(-2.0, lower_ccf_boundary + 1e-6), 3.0)
        q2 = rng.uniform(max(-2.0, lower_ccf_boundary + 1e-6), 3.0)
        ead_min = min(drawn + q1 * undrawn, drawn + q2 * undrawn)
        loss = rng.uniform(0.0, ead_min)
        pd = rng.uniform(0.0001, 0.4)
        maturity = rng.uniform(1.0, 5.0)
        first = Allocation(drawn, undrawn, q1, loss, pd, maturity)
        second = Allocation(drawn, undrawn, q2, loss, pd, maturity)
        rwa_first = corporate_rwa(pd, first.realised_lgd, first.ead, maturity)
        rwa_second = corporate_rwa(pd, second.realised_lgd, second.ead, maturity)
        error = abs(rwa_first - rwa_second)
        maximum_raw_error = max(maximum_raw_error, error)
        if not math.isclose(rwa_first, rwa_second, rel_tol=1e-11, abs_tol=1e-9):
            raw_failures.append(case_id)
        floor = rng.uniform(0.01, 0.30)
        floored_first = corporate_rwa(pd, first.operational_lgd(floor=floor), first.ead, maturity)
        floored_second = corporate_rwa(pd, second.operational_lgd(floor=floor), second.ead, maturity)
        if not math.isclose(floored_first, floored_second, rel_tol=1e-11, abs_tol=1e-9):
            floor_breaks += 1

    pd_grid = [0.001 + index * (0.998 / 20000) for index in range(20001)]
    pd_values = [corporate_capital_per_ead(pd, 0.45, 2.5) for pd in pd_grid]
    maximum_index = max(range(len(pd_values)), key=pd_values.__getitem__)
    report = {
        "claim_status": "numerically_verified_on_stated_finite_set",
        "seed": SEED,
        "random_cases": CASES,
        "raw_invariance_failures": raw_failures,
        "maximum_raw_absolute_error": maximum_raw_error,
        "floor_break_count": floor_breaks,
        "pd_grid": {
            "lower": 0.001,
            "upper": 0.999,
            "points": len(pd_grid),
            "maximizer_on_grid": pd_grid[maximum_index],
            "maximum_capital_per_ead_on_grid": pd_values[maximum_index],
            "lgd": 0.45,
            "maturity": 2.5,
        },
        "tolerances": {"relative": 1e-11, "absolute": 1e-9},
    }
    report_dir = ROOT / "artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    output = report_dir / "adversarial-atlas.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = run_manifest(
        command=["python3", "experiments/run_adversarial_atlas.py"],
        inputs=[
            Path(__file__).resolve(),
            ROOT / "src" / "capital_consistency" / "__init__.py",
            ROOT / "src" / "capital_consistency" / "audit.py",
            ROOT / "src" / "capital_consistency" / "decompositions.py",
            ROOT / "src" / "capital_consistency" / "irb.py",
            ROOT / "src" / "capital_consistency" / "numeric.py",
        ],
        outputs=[output],
        assumptions=[
            "corporate performing-exposure IRB test functional",
            "random cases use fixed loss, PD, maturity and only vary CCF allocation",
            "PD result is a finite grid, not a certified global optimizer",
        ],
        project_dir=ROOT,
        solver="deterministic seeded random enumeration plus finite PD grid",
        solver_status="completed on the stated finite sample and grid",
        arithmetic="IEEE-754 floating point",
        claim_status="finite numerical regression evidence, not proof or certified global optimization",
        tolerances={"relative": 1e-11, "absolute": 1e-9},
        random_seed=SEED,
    )
    (report_dir / "adversarial-atlas-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"raw_failures": len(raw_failures), "floor_breaks": floor_breaks, "seed": SEED}))


if __name__ == "__main__":
    main()
