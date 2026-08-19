"""Command-line interface for the auditable core."""

import argparse
import json
import runpy
from pathlib import Path

from .certificates import verify_certificate
from .decompositions import Allocation
from .expected_loss import expected_loss
from .irb import corporate_rwa
from .optimization import AllocationIntervalProblem, sharp_operational_product_bounds
from .schemas import EconomicHistory
from .uncertainty_sets import ellipsoid_affine_upper


def _load(path: str):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def cmd_validate_history(args) -> int:
    history = EconomicHistory.from_dict(_load(args.file))
    print(json.dumps({"valid": True, "history_id": history.history_id, "schema_version": history.schema_version}))
    return 0


def cmd_evaluate_allocation(args) -> int:
    allocation = Allocation(**_load(args.file))
    allocation.validate()
    if args.lgd_upper_clip is None:
        operational_lgd = max(args.lgd_floor, allocation.realised_lgd)
        lgd_mode = "raw_or_floored_without_upper_clip"
    else:
        operational_lgd = allocation.operational_lgd(
            floor=args.lgd_floor, upper_clip=args.lgd_upper_clip
        )
        lgd_mode = "floored_and_upper_clipped"
    result = {
        "ead": allocation.ead,
        "realised_lgd": allocation.realised_lgd,
        "operational_lgd": operational_lgd,
        "lgd_mode": lgd_mode,
        "expected_loss": expected_loss(allocation, args.lgd_floor, args.lgd_upper_clip),
    }
    if 0.0 <= operational_lgd <= 1.0:
        result["rwa"] = corporate_rwa(allocation.pd, operational_lgd, allocation.ead, allocation.maturity)
        result["rwa_status"] = "evaluated"
    else:
        result["rwa"] = None
        result["rwa_status"] = "LGD outside corporate test domain [0,1]; supply an explicit admissible clip"
    print(json.dumps(result, sort_keys=True))
    return 0


def cmd_enumerate_decompositions(args) -> int:
    data = _load(args.file)
    rows = []
    for ccf in data["ccf_values"]:
        allocation = Allocation(
            drawn=data["drawn"],
            undrawn=data["undrawn"],
            ccf=ccf,
            economic_loss=data["economic_loss"],
            pd=data["pd"],
            maturity=data.get("maturity", 2.5),
        )
        allocation.validate()
        rows.append({"ccf": ccf, "ead": allocation.ead, "realised_lgd": allocation.realised_lgd})
    print(json.dumps({"decompositions": rows}, sort_keys=True))
    return 0


def cmd_extremize_allocation(args) -> int:
    problem = AllocationIntervalProblem(**_load(args.file))
    lower, upper = sharp_operational_product_bounds(problem)
    print(
        json.dumps(
            {
                "lower": lower,
                "upper": upper,
                "lower_endpoint_ccf": problem.ccf_lower,
                "upper_endpoint_ccf": problem.ccf_upper,
                "certificate": "monotone endpoint reduction",
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_solve_joint_moc(args) -> int:
    data = _load(args.file)
    upper = ellipsoid_affine_upper(data["center"], data["covariance"], data["gradient"], data["radius"])
    print(json.dumps({"affine_risk_upper": upper}, sort_keys=True))
    return 0


def cmd_verify_certificate(args) -> int:
    valid = verify_certificate(Path(args.file))
    print(json.dumps({"valid": valid}))
    return 0 if valid else 1


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_reproduce(args) -> int:
    if args.experiment_id != "core-exact":
        raise ValueError("unknown experiment_id")
    runpy.run_path(
        str(_project_root() / "experiments" / "run_exact_examples.py"),
        run_name="__main__",
    )
    return 0


def cmd_audit(args) -> int:
    certificate_dir = _project_root() / "artifacts" / "certificates"
    results = {path.name: verify_certificate(path) for path in sorted(certificate_dir.glob("*.json"))}
    valid = bool(results) and all(results.values())
    print(json.dumps({"valid": valid, "certificates": results}, sort_keys=True))
    return 0 if valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capital-consistency")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-history")
    validate.add_argument("file")
    validate.set_defaults(function=cmd_validate_history)
    evaluate = subparsers.add_parser("evaluate-allocation")
    evaluate.add_argument("file")
    evaluate.add_argument("--lgd-floor", type=float, default=0.0)
    evaluate.add_argument(
        "--lgd-upper-clip",
        type=float,
        default=None,
        help="explicit LGD upper cap; omitted means no implicit cap",
    )
    evaluate.set_defaults(function=cmd_evaluate_allocation)
    enumerate_parser = subparsers.add_parser("enumerate-decompositions")
    enumerate_parser.add_argument("file")
    enumerate_parser.set_defaults(function=cmd_enumerate_decompositions)
    extremize = subparsers.add_parser("extremize-allocation")
    extremize.add_argument("file")
    extremize.set_defaults(function=cmd_extremize_allocation)
    solve = subparsers.add_parser("solve-joint-moc")
    solve.add_argument("file")
    solve.set_defaults(function=cmd_solve_joint_moc)
    verify = subparsers.add_parser("verify-certificate")
    verify.add_argument("file")
    verify.set_defaults(function=cmd_verify_certificate)
    reproduce = subparsers.add_parser("reproduce")
    reproduce.add_argument("experiment_id")
    reproduce.set_defaults(function=cmd_reproduce)
    audit = subparsers.add_parser("audit")
    audit.set_defaults(function=cmd_audit)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
