# Running Instructions

This project is organized around the focused renewables analysis in `focused_renewables_analysis/`.

## Requirements

Install the Python packages used by the scripts:

```bash
python3 -m pip install pandas numpy matplotlib statsmodels
```

The notebooks additionally require Jupyter if you want to open or rerun them interactively:

```bash
python3 -m pip install notebook
```

## Running in GitHub Codespaces

Open the repo in Codespaces, then run these commands from the terminal:

```bash
python3 -m pip install pandas numpy matplotlib statsmodels notebook
python3 focused_renewables_analysis/scripts/renewables_decomposition_lagged.py
```

The script should finish without needing any manual file downloads because the required raw and derived renewable energy CSV files are already included in the repo.

To view the generated charts in Codespaces, open:

```text
focused_renewables_analysis/outputs/
```

To inspect or rerun the notebooks, open the `.ipynb` files in:

```text
focused_renewables_analysis/notebooks/
```

## Main Analysis

From the project root, run:

```bash
python3 focused_renewables_analysis/scripts/renewables_decomposition_lagged.py
```

This regenerates the focused outputs in:

```text
focused_renewables_analysis/outputs/
```

Key outputs include:

- `lagged_capacity_models.csv`
- `lagged_capacity_wind_gen.png`
- `lagged_capacity_solar_gen.png`
- `lagged_capacity_renew_share_elec.png`
- `renewable_share_decomposition.csv`
- `renewable_share_decomposition.png`

## Data

Raw renewable energy source files are in:

```text
data/raw_renewables/
```

Merged analysis datasets are in:

```text
data/derived_renewables/
```

## Notebooks

The main notebooks are:

- `focused_renewables_analysis/notebooks/merging_data_notebook.ipynb`
- `focused_renewables_analysis/notebooks/regression_analysis.ipynb`

These document the data preparation, exploratory analysis, and baseline fixed-effects regression work.
