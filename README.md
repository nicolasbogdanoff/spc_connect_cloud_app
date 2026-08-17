# SPC Connect — X̄-R Control Charts and Process Capability

A Shiny for Python application for exploratory statistical process control (SPC), built around X̄-R control charts and process-capability analysis.

The project is designed for engineering education, process analysis, and transparent experimentation with subgrouped measurements. It keeps the full analytical trace visible: observations excluded from revised limit estimation remain displayed on the revised charts.

[![Tests](https://github.com/nicolasbogdanoff/spc_connect_cloud_app/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolasbogdanoff/spc_connect_cloud_app/actions/workflows/tests.yml)

## What it does

- Builds X̄-R charts for subgroup sizes from 2 to 10 measurements.
- Estimates initial control limits using the standard A2, D3, D4, and d2 constants.
- Supports manual exclusion of subgroups associated with an investigated assignable cause.
- Provides an automatic diagnostic mode that flags initial out-of-limit subgroups for review.
- Recalculates revised limits without silently removing excluded observations from the charts.
- Reports initial and revised signals for both the X̄ and R charts.
- Calculates Cp, Cpk, Pp, Ppk, CPL, CPU, PPL, PPU, and an estimated within-process PPM.
- Imports CSV, XLSX, and XLS files.
- Exports subgroup statistics, control limits, and capability results to Excel.
- Includes a reproducible sample dataset based on the project’s reference SPC exercise.

## Methodology

The application follows this workflow:

1. Normalize the input data and validate the subgroup identifiers and measurement columns.
2. Calculate each subgroup mean and range.
3. Estimate initial X̄-R limits from all available subgroups.
4. Apply either a manually specified exclusion list or the automatic diagnostic selection.
5. Re-estimate revised limits from the retained subgroups.
6. Keep every subgroup visible in the revised charts so the analytical history remains auditable.
7. Estimate process capability from the retained measurements.

For within-subgroup variation, the application estimates sigma as R̄/d2. Overall variation is calculated from the retained observations using the sample standard deviation. Capability and expected PPM values assume a normal approximation and should be interpreted together with process knowledge and engineering judgment.

> An out-of-limit observation is a signal for investigation, not by itself a justification for deleting data. Any exclusion should be supported by an identified assignable cause.

## Quick start

### Requirements

- Python 3.10 or newer
- pip

### Install and run

~~~bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
shiny run --reload app.py
~~~

Then open the local URL shown by the terminal, usually http://127.0.0.1:8000.

## Input format

The application expects one row per subgroup:

~~~csv
Subgrupo,x1,x2,x3,x4
1,459,449,435,450
2,443,440,442,442
~~~

The first column is used as the subgroup identifier. The remaining measurement columns must be numeric, complete, and contain between 2 and 10 measurements per subgroup.

For the included sample data, the default specification values are:

- LSL: 420
- Target: 450
- USL: 480

The sample interface initially shows subgroup 18 as a manually excluded subgroup. Change this setting when analyzing a different dataset.

## Using the application

1. Choose the included sample or upload a CSV/Excel file.
2. Select manual exclusion or the automatic diagnostic mode.
3. If using manual mode, enter subgroup identifiers separated by commas.
4. Enter the lower specification limit, target, and upper specification limit.
5. Review the initial and revised X̄-R charts.
6. Inspect capability indices and the numerical results.
7. Export the analysis workbook when a record of the calculation is required.

The revised chart uses shading and an orange outline to distinguish subgroups excluded from limit estimation while keeping them visible.

## Repository layout

| File | Purpose |
| --- | --- |
| app.py | Shiny for Python application and SPC calculations |
| sample_data.csv | Included subgrouped example data |
| styles.css | Application styling |
| requirements.txt | Runtime dependencies |
| DEPLOYMENT.md | Posit Connect Cloud deployment notes |
| CITATION.cff | Citation metadata for scholarly or technical reuse |
| LICENSE | MIT license |

## Testing

The repository includes regression tests for sample-data normalization, manual exclusion traceability, capability calculations, and specification-limit validation. Run them locally with:

~~~bash
pip install -r requirements.txt pytest
pytest -q
~~~

## Deployment

See DEPLOYMENT.md for the Posit Connect Cloud workflow and troubleshooting notes.

## Scope and limitations

This repository is intentionally focused on a compact, inspectable SPC application. It does not provide authentication, persistence, database storage, automated process governance, or a substitute for a validated quality-management system. Before using results for operational decisions, verify the measurement system, subgrouping strategy, specification limits, distributional assumptions, and the engineering context of any assignable causes.

## Author

**Nicolás Mauricio Bogdanoff**  
Engineering education and research interests spanning scientific computing, statistical quality, and applied engineering analysis.

- ORCID: https://orcid.org/0009-0004-6275-3013
- GitHub: https://github.com/nicolasbogdanoff

## Citation

If this software contributes to a technical report, class activity, research note, or publication, cite it using [CITATION.cff](CITATION.cff).

## License

This project is released under the [MIT License](LICENSE).
