# Capital Consistency under Regulatory Credit-Risk Uncertainty

Exact examples, boundary results, and auditable computations for CCF/EAD-LGD
allocation and joint margins of conservatism in an EU IRB research setting.

> **Research and software status**
>
> Experimental technical research implementation. It is not a validated bank
> capital engine, a substitute for supervisory software, or legal, regulatory,
> statistical, accounting, or risk-management advice. The implemented
> Basel-style corporate functional is a mathematical test functional; its legal
> applicability and operator order must be checked independently for each use.

**[Read the technical report](artifacts/reports/capital-consistency-technical-report.pdf).**

The project asks two connected but bounded questions:

1. When does reallocating one fixed synthetic economic history between
   exposure at default/credit conversion factor and realised LGD preserve
   expected loss or RWA expressions?
2. Once a valid joint uncertainty set has been specified, what deterministic
   calculations bound capital-scale targets without silently replacing joint
   coverage by unrelated component-wise margins?

The package uses only the Python standard library. It includes exact rational
counterexamples, a separately checked corporate IRB formula, small support and
endpoint solvers, deterministic synthetic experiments, and three machine-readable
certificates.

## Main result and its boundary

For one fixed economic history, consider

$$
R(\theta,q)=c(\theta)\,\psi_{\ell,u}(A(q),L),
\qquad
\psi_{\ell,u}(A,L)=\min\{uA,\max(\ell A,L)\}.
$$

Within the paper’s stated separable, nonnegative domain:

- if no floor or clip binds, loss consistency $A(q)g(q)=L$ removes the
  allocation choice from the product exactly;
- with a common floor/clip and interval CCF, the allocation maximum reduces to
  the maximum-EAD endpoint;
- when allocation changes PD, maturity, grade, segment, weights, operators, or
  the uncertainty set, factorization and endpoint reduction can fail.

This is a boundary characterization, not a claim that the elementary
$\mathrm{EAD}\times\mathrm{LGD}$ identity or regulatory compensation principle
is new, and not a universal capital-invariance theorem.

## Joint conservatism

The implementation treats two questions as separate:

1. Does a supplied confidence or uncertainty set have the intended simultaneous
   validity?
2. Given that set, what is the worst value of the actual regulatory target?

Projection, ellipsoid support, Bonferroni bounds, finite transport, and robust
optimization are established methods. The current package implements useful
special cases and counterexamples; it does not supply a credit-specific
finite-sample joint-coverage theorem for dependent PD/LGD/CCF estimators.

In particular, the implemented corporate unexpected-loss kernel is not
globally increasing in PD, so a component-wise upper PD need not maximize RWA.
Direct target optimization is required on the stated domain.

## Reproduce the release

Requirements: Python 3.9+ and a POSIX shell. No third-party Python package,
database, external service, credential, or confidential dataset is needed.

```sh
make test
make reproduce
make audit
```

Equivalent direct commands:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -m unittest discover -s tests -p 'test_*.py' -v
bash scripts/reproduce_all.sh
bash scripts/audit_repository.sh
```

The release audit runs 36 tests, regenerates the exact examples and seeded
adversarial atlas, independently checks all three certificates, and rejects
unexpected symlinks or generated interpreter/log artifacts.

The adversarial atlas contains 5,000 seeded reallocation pairs and a
20,001-point PD grid. Those are finite numerical regression results, not proofs
or certified global optimization. Exact-rational status applies only to the
certificates that explicitly claim it.

## Command-line interface

Install the local package:

```sh
python3 -m pip install -e .
capital-consistency --help
```

Representative commands:

```sh
capital-consistency validate-history examples/cashflow-histories/repeat-default.json
capital-consistency evaluate-allocation \
  examples/exact-counterexamples/allocation-low-ead.json --lgd-floor 0.10
capital-consistency extremize-allocation \
  examples/mathematical-edge-cases/allocation-interval.json
capital-consistency verify-certificate \
  artifacts/certificates/allocation-floor-counterexample.json
capital-consistency reproduce core-exact
capital-consistency audit
```

All bundled examples are synthetic.

## Certificates and artifacts

`artifacts/certificates/` contains:

- an exact rational LGD-floor allocation counterexample;
- an exact rational default-weighting counterexample; and
- a floating ellipsoid-support certificate with an independent semantic check.

`artifacts/reports/` contains the reviewed paper, deterministic manifests, and
the finite adversarial atlas. Manifests use content hashes and deliberately
record no private Git commit identifier.

## Prior work and regulatory attribution

The report explicitly credits and distinguishes:

- [CRR3, Regulation (EU) 2024/1623](https://eur-lex.europa.eu/eli/reg/2024/1623/oj)
  and the [consolidated CRR](https://eur-lex.europa.eu/eli/reg/2013/575/2026-06-26/eng);
- [EBA/GL/2017/16](https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-final-guidelines-estimation-risk-parameters)
  on PD/LGD estimation and defaulted exposures;
- the consultative, non-binding [EBA CCF methodology material](https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-methodology-estimate-and-apply-credit-conversion-factors-under-capital-requirements?version=2025);
- the Basel Committee’s [CRE31 risk-weight-function specification](https://www.bis.org/basel_framework/chapter/CRE/31.htm);
- Kaido, Molinari, and Stoye on projection inference;
- Delage and Ye on distributionally robust optimization;
- Löffler and Baviera on estimation/model risk in credit capital.

Regulatory texts, guidance, and consultation material are not interchangeable.
Their citation does not imply endorsement, legal validation, or co-authorship.
The bibliography and regulatory-scope note state the project’s access-date and
operator-order limitations.

## Documentation

- [`docs/regulatory-scope.md`](docs/regulatory-scope.md) — legal hierarchy and scope boundary
- [`docs/mathematical-conventions.md`](docs/mathematical-conventions.md) — domains and operators
- [`docs/reproducibility.md`](docs/reproducibility.md) — network-free audit commands
- [`docs/glossary.md`](docs/glossary.md) — terminology
- [`docs/open-questions.md`](docs/open-questions.md) — unresolved research and application limits

## Repository layout

```text
src/capital_consistency/    dependency-free implementation and CLI
tests/                      36 unit, exact, adversarial, and regression tests
experiments/                deterministic certificate/atlas generators
examples/                   synthetic histories and edge cases
artifacts/certificates/     reviewed machine-readable witnesses
artifacts/reports/          technical report and deterministic manifests
docs/                       public scope and reproducibility documentation
scripts/                    portable reproduction and release audit
```

Research notebooks, working logs, novelty matrices, LaTeX source, local
automation instructions, and duplicate release trees are not distributed in
this repository.

## Limitations

- The simple product identity requires the exact assumptions stated in the
  report; separately estimated CCF and LGD need not satisfy recordwise loss
  consistency.
- Floors, clipping, weighting, aggregation, grading, segmentation, and model
  coupling can change the result.
- The corporate functional does not establish EU legal applicability for a
  particular exposure class.
- Full nonlinear portfolio optimization is not globally certified.
- Joint-MoC calculations remain conditional on a valid supplied uncertainty
  set and action class.
- Source review was targeted, not an exhaustive priority search.

## Citation and license

Use [`CITATION.cff`](CITATION.cff) to cite the technical report and versioned
software release. The implementation is available under the [MIT License](LICENSE).
Regulatory texts and cited academic works retain their own authorship and terms.
