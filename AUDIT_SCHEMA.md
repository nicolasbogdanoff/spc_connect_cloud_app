# JSON audit summary

SPC Connect can export a machine-readable audit summary alongside the Excel workbook. The JSON is intended for review, issue reports, reproducibility notes, and downstream tooling.

## Stability

The top-level `schema_version` identifies the shape of the export. Consumers should reject or explicitly handle versions they do not support. New fields may be added without changing the meaning of existing fields; a breaking field change requires a new schema version.

## Top-level fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer version of this JSON contract. |
| `application` | Application name that produced the export. |
| `method` | Statistical method, currently `Xbar-R`. |
| `exclusion_mode` | `manual` or `auto`, matching the selected analysis mode. |
| `measurement_columns` | Numeric measurement columns used for each subgroup. |
| `measurements_per_subgroup` | Number of measurements in each subgroup. |
| `subgroups_total` | Number of input subgroups. |
| `subgroups_used_for_revised_limits` | Number retained to estimate revised limits. |
| `observations_used` | Number of retained individual measurements used for capability. |
| `excluded_subgroups` | Subgroup identifiers excluded from revised-limit estimation. |
| `signals` | Initial and revised X̄, R, and X̄ run signals. |
| `specifications` | LSL, target, and USL used for capability calculations. |
| `limits` | Initial and revised X̄-R control-limit dictionaries. |
| `capability` | Cp, Cpk, Pp, Ppk, sigma within, and sigma overall. |
| `stable_revised` | Whether the revised analysis has no additional X̄, R, or run signals. |

## Interpretation

An excluded subgroup remains visible in the charts and in the exported subgroup table. Exclusion is a traceable analytical decision, not an assertion that the observation was invalid. Signal fields identify points requiring investigation; they do not automatically diagnose a cause or authorize data deletion.

Capability indices use the retained observations and the assumptions described in the main README. Consumers should preserve the specifications, limits, exclusions, and signals together rather than treating a single index as a standalone quality decision.
