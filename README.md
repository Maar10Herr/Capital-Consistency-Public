# Capital Consistency

[![CI](https://github.com/Maar10Herr/Capital-Consistency-Public/actions/workflows/ci.yml/badge.svg)](https://github.com/Maar10Herr/Capital-Consistency-Public/actions/workflows/ci.yml)
[![License: GPL v3+](https://img.shields.io/badge/License-GPL_v3%2B-blue.svg)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--8721--6588-A6CE39.svg)](https://orcid.org/0009-0005-8721-6588)

Exact allocation identities, regulatory boundary cases, and joint-conservatism
tools for European internal-ratings credit-risk calculations.

> [!IMPORTANT]
> **Research software and technical report.** The regulatory mapping is tied to
> the cited CRR3 and EBA materials. Operational use requires independent legal,
> model-risk, and implementation review for the relevant exposure class and
> reporting date.

**[Read the technical report](artifacts/reports/capital-consistency-technical-report.pdf)** ·
**[Download the latest release](https://github.com/Maar10Herr/Capital-Consistency-Public/releases/latest)**

## Results at a glance

The project studies how a fixed economic history changes when loss is allocated
between exposure at default (EAD), credit conversion factor (CCF), and loss
given default (LGD).

For loss-consistent records with `EAD × LGD = L`, expected loss and the
performing-exposure IRB capital term reduce to weighted moments of the same
economic-loss atoms:

```math
\mathrm{EL}=\sum_i w_i p_i L_i,
\qquad
\mathrm{RWA}_0=12.5\sum_i w_i L_i H(p_i,M_i,s_i).
```

This yields four concrete results:

1. **Exact invariance criteria.** Allocation is immaterial precisely when the
   corresponding weighted loss moments remain fixed.
2. **Sharp endpoint reduction.** Under common LGD floors or clips and interval
   CCF uncertainty, the worst allocation is attained at the maximum feasible
   EAD endpoint.
3. **Boundary counterexamples.** Exact rational witnesses show how binding
   floors, default weighting, and coefficient-changing transfers break simple
   product invariance.
4. **Joint conservatism discipline.** Confidence-set validity and worst-case
   target optimization are separate steps; the corporate unexpected-loss
   coefficient must be optimized directly because it is not globally
   increasing in PD.

The unified collapse-or-endpoint theorem identifies when allocation uncertainty
disappears, when it becomes a one-endpoint calculation, and when grade, segment,
weight, or confidence-set coupling requires joint optimization.

## Quick start

The core package uses the Python standard library and supports Python 3.9+.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
capital-consistency --help
```

Run the exact examples and verify every certificate:

```sh
python3 experiments/run_exact_examples.py
python3 -m capital_consistency verify-all artifacts/certificates
```

Reproduce the complete public evidence set:

```sh
make reproduce
make audit
```

## Evidence package

| Artifact | Purpose | Verification status |
|---|---|---|
| `allocation-floor-counterexample.json` | Binding-floor witness | Exact rational recomputation |
| `allocation-weighting-counterexample.json` | Default-weighting witness | Exact rational recomputation |
| `ellipsoid-affine-support.json` | Affine support over a singular ellipsoid | Independent primal/upper-bound check |
| `adversarial-atlas.json` | Fixed-loss reallocations and PD-grid regressions | Deterministic finite test atlas |
| Technical report | Definitions, theorems, proofs, and regulatory scope | Built, linked, and cited from the release |

The adversarial atlas fixes seed `20260806`, evaluates 5,000 random reallocation
pairs, and checks a 20,001-point PD grid. Algebraic claims are proved in the
report; rational status applies to the two exact certificates.

## Package structure

```text
src/capital_consistency/   formulas, allocation model, uncertainty sets, CLI
artifacts/certificates/    machine-readable verification targets
artifacts/reports/         paper and deterministic experiment manifests
experiments/               exact examples and adversarial atlas
examples/                  synthetic histories, portfolios, and edge cases
docs/                      conventions, regulatory scope, and reproducibility
tests/                     unit, exact, adversarial, property, and regression tests
```

The independent IRB checker has separate normal-CDF and inverse-normal
implementations. Certificate verification reconstructs each claim from source
records and independently coded formulas.

## Regulatory and research foundations

The product compensation principle is already present in European regulation
and supervisory guidance. This project contributes a formal boundary atlas,
exact counterexamples, and a joint-uncertainty formulation around that
principle.

Primary regulatory sources:

- [Regulation (EU) 2024/1623 (CRR3)](https://eur-lex.europa.eu/eli/reg/2024/1623/oj)
- [Consolidated Regulation (EU) No 575/2013](https://eur-lex.europa.eu/eli/reg/2013/575/oj)
- [EBA/GL/2017/16: PD and LGD estimation and the treatment of defaulted exposures](https://www.eba.europa.eu/regulation-and-policy/model-validation/guidelines-on-pd-lgd-estimation-and-treatment-of-defaulted-exposures)

Statistical and optimization context includes support-function inference,
distributionally robust optimization, and parameter uncertainty in credit-risk
capital:

- Kaido, Molinari & Stoye, *Econometrica* 87 (2019),
  [doi:10.3982/ECTA14075](https://doi.org/10.3982/ECTA14075)
- Delage & Ye, *Operations Research* 58 (2010),
  [doi:10.1287/opre.1090.0741](https://doi.org/10.1287/opre.1090.0741)
- Löffler, *Journal of Banking & Finance* 27 (2003),
  [doi:10.1016/S0378-4266(02)00277-7](https://doi.org/10.1016/S0378-4266(02)00277-7)

Full citations and the precise relation of each source to the results appear in
the report.

## Verification

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
bash scripts/reproduce_all.sh
bash scripts/audit_repository.sh
```

The audit checks all certificates, deterministic manifests, repository
boundaries, malformed inputs, cleanup behavior, and the independent formula
cross-checks.

## Citation

Use the preferred paper citation in [`CITATION.cff`](CITATION.cff) and cite the
specific release used. Author:
[Maarten Linus Herrmann](https://orcid.org/0009-0005-8721-6588), ORCID
[`0009-0005-8721-6588`](https://orcid.org/0009-0005-8721-6588).

## License

The software is licensed under [GPL-3.0-or-later](LICENSE). The technical report
is copyright © 2026 Maarten Linus Herrmann; all rights reserved. Copyleft keeps
distributed modifications to the certificate and formula implementation under
the same reciprocal terms. Regulatory texts and cited publications remain
subject to their original terms.
