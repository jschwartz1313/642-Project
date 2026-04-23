# Focused Renewables Analysis

This folder collects the materials most relevant to the narrowed project scope:

- data preparation and sample construction
- exploratory analysis of renewable trends
- baseline fixed-effects regression
- lagged capacity models
- renewable-share decomposition
- K-means clustering
- XGBoost prediction benchmarking

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
- `advanced_cluster_metrics.csv`
  K-means model-selection metrics for the clustering extension.
- `advanced_cluster_summary.csv`
  Summary statistics for the country clusters used in the focused project.
- `advanced_country_clusters.csv`
  Country-level cluster assignments and feature values.
- `advanced_country_clusters_pca.png`
  PCA visualization of the focused-project clusters.
- `advanced_xgboost_metrics.csv`
  Out-of-sample MAE and RMSE comparing linear regression and XGBoost.
- `advanced_xgboost_feature_importance.csv`
  XGBoost feature-importance rankings for renewable-share prediction.
- `advanced_xgboost_feature_importance.png`
  Plot of the feature-importance results.
- `advanced_xgboost_predictions.csv`
  Test-period predictions from the XGBoost model.
- `advanced_xgboost_predictions_by_country.png`
  Country-level plot comparing predicted and actual renewable share.
- `advanced_nonlinear_fe_coefficients.csv`
  Coefficients from the nonlinear fixed-effects extensions.
- `advanced_nonlinear_fe_coefficients.png`
  Visualization of the nonlinear fixed-effects coefficients.
- `advanced_nonlinear_fe_model_summary.csv`
  Model-comparison summary for the nonlinear fixed-effects specifications.

## What is intentionally left out

This folder does not include the separate GDP analysis track or the older exploratory ARIMA/clustering work preserved under `side_analyses/`. Those materials are still useful as reference, but the current final project story lives in this folder.

## Recommended presentation flow

1. Explain how the 17 source files were merged and narrowed to the usable country sample.
2. Show the main renewable trends and why fixed effects are needed.
3. Present the baseline generation and share regressions.
4. Use the lagged models and decomposition to interpret the share results.
5. Add the clustering and XGBoost extensions as supporting evidence for the broader transition story.
