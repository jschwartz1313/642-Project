# Focused Renewables Analysis

This folder collects the materials most relevant to the narrowed project scope:

- data preparation and sample construction
- exploratory analysis of renewable trends
- baseline fixed-effects regression
- lagged capacity models

The goal of this reduced scope is to keep the project centered on one connected question:

How do wind and solar capacity relate to renewable electricity generation and renewable electricity share across countries, and do those effects appear with a lag?

## Folder contents

`notebooks/`

- `merging_data_notebook.ipynb`
  Builds the merged datasets and shows the country-overlap and missingness logic.
- `regression_analysis.ipynb`
  Contains the main EDA and baseline fixed-effects regression models.

`scripts/`

- `renewables_decomposition_lagged.py`
  Generates the lagged-capacity models and the renewable-share decomposition outputs.
  This script reads from `../data/derived_renewables/` at the repo level.

`outputs/`

- `lagged_capacity_models.csv`
  Regression coefficients for contemporaneous and 1- to 3-year lagged capacity models.
- `lagged_capacity_wind_gen.png`
  Wind-capacity lag coefficients for wind generation.
- `lagged_capacity_solar_gen.png`
  Solar-capacity lag coefficients for solar generation.
- `lagged_capacity_renew_share_elec.png`
  Lagged-capacity coefficients for renewable electricity share.
- `renewable_share_decomposition.csv`
  Country-level decomposition of renewable-share change into wind, solar, hydro, and other components.
- `renewable_share_decomposition.png`
  Visual summary of that decomposition.

## What is intentionally left out

This folder does not include the GDP analysis, ARIMA forecasting outputs, or K-means clustering outputs. Those analyses still exist under `side_analyses/`, but they are not part of the narrow core story.

## Recommended presentation flow

1. Explain how the 17 source files were merged and narrowed to the usable country sample.
2. Show the main renewable trends and why fixed effects are needed.
3. Present the baseline generation and share regressions.
4. Use the lagged models as the main extension.
5. If needed, use the decomposition as one supporting interpretation slide.
