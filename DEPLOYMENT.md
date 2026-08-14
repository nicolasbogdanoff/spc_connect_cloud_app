# Deployment

This application is built with Shiny for Python and is structured for deployment from the repository root.

## Local validation

Create a virtual environment and install the pinned dependency ranges:

~~~bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
shiny run --reload app.py
~~~

Open the local address reported by the terminal, usually http://127.0.0.1:8000.

Before publishing, confirm that:

- the sample dataset loads;
- both initial and revised X̄-R charts render;
- CSV and Excel upload paths behave as expected;
- capability results are produced for valid specification limits;
- the Excel download contains the expected result sheets.

## Posit Connect Cloud

The repository contains the files required by the Shiny for Python deployment:

- app.py
- requirements.txt
- sample_data.csv
- styles.css
- README.md
- DEPLOYMENT.md
- CITATION.cff

A typical publication flow is:

1. Sign in to Posit Connect Cloud.
2. Choose Publish and connect the GitHub account when prompted.
3. Select nicolasbogdanoff/spc_connect_cloud_app.
4. Select the main branch.
5. Choose Shiny for Python as the framework.
6. Set app.py as the application entry point.
7. Publish and wait for dependency installation to complete.

The deployment should keep the repository root as the working directory because app.py loads sample_data.csv and styles.css from its own directory.

## Updating a deployment

After changing the application or documentation:

~~~bash
git add .
git commit -m "Describe the change"
git push
~~~

Republish from Posit Connect Cloud or use the repository integration if automatic deployment is enabled.

## Troubleshooting

### Dependency installation fails

Check that requirements.txt is present at the repository root and that each dependency appears on its own line.

### The sample data or stylesheet is missing

Keep sample_data.csv and styles.css beside app.py. The application resolves both files relative to its own directory.

### Excel export fails

Confirm that openpyxl is installed from requirements.txt.

### The chart does not match the reference analysis

For the included sample data, use:

- exclusion mode: Manual;
- excluded subgroup: 18;
- LSL: 420;
- target: 450;
- USL: 480.

The revised chart intentionally keeps subgroup 18 visible while excluding it from revised-limit estimation. This preserves traceability and should not be interpreted as permission to remove an observation without an assignable cause.
