# 642 Project

This repo is now organized to separate the core presentation-ready renewables analysis from side analyses and archived duplicates.

## What to use

If you are working on the narrowed final project, start in:

- `focused_renewables_analysis/`

That folder contains the materials most relevant to the current project scope:

- data/sample framing through the copied notebooks
- baseline fixed-effects regression
- lagged capacity models
- renewable-share decomposition as supporting interpretation
- nonlinear fixed-effects extensions
- K-means clustering
- XGBoost prediction benchmarking

## Folder guide

`data/`

- `raw_renewables/`: original source CSV files
- `derived_renewables/`: merged datasets used by the analysis scripts

`focused_renewables_analysis/`

- the main folder for the final project story, including the presentation-ready extensions

`side_analyses/`

- `real_gdp/`: the separate GDP analysis track
- `renewables_forecasting_clustering/`: older exploratory renewables ARIMA and clustering analyses kept for reference

`project_materials/`

- proposal, presentations, and presentation-building scripts

`archive/`

- legacy notebooks that used to live at the repo root
- duplicate outputs/scripts kept for reference but not needed for the focused project

## Recommended focus

The cleanest project question is:

How do wind and solar capacity expansions relate to renewable electricity generation and renewable electricity share across countries, and do those effects appear with a lag?

That means the most important materials are in:

- `focused_renewables_analysis/notebooks/`
- `focused_renewables_analysis/scripts/`
- `focused_renewables_analysis/outputs/`
