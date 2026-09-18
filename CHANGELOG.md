# Changelog

## 0.4.0 — 2026-09-18

- Rejected fractional, non-finite, partially missing, and ambiguous subgroup or measurement inputs before statistical calculation.
- Added explicit validation for the selected exclusion mode.
- Added Ruff linting and a Python 3.10–3.12 CI matrix.

## 0.3.0 — 2026-09-18

- Versioned the JSON audit summary with application metadata, measurement columns, observation counts, exclusion mode, and initial/revised control limits.
- Added regression coverage for non-finite specifications and zero-variability datasets.
- Capability analysis now rejects non-finite specifications and retained datasets without positive variation with explicit user-facing errors.

## 0.2.0 — 2026-09-16

- Added a JSON audit export for specifications, exclusions, signals, and capability metrics.
- Added eight-point X̄ run-signal detection as a review prompt.
- Added contribution, security, issue, and pull-request guidance for maintainers.

## 0.1.0 — 2026-08-17

- Documented the X̄-R control-chart and process-capability workflow.
- Added reproducible regression tests for sample-data normalization and manual exclusion traceability.
- Added continuous integration through GitHub Actions.
- Added an MIT license and citation metadata for technical reuse.
