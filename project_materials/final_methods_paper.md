# Methods Used to Analyze Renewable Electricity Growth

## Introduction

This project examines how the expansion of wind and solar capacity relates to renewable electricity generation and renewable electricity share across countries. The original data collection contained many renewable energy indicators, including renewable generation, installed capacity, and the percentage of electricity generated from wind, solar, hydro, and other renewable sources. Because the full set of files varied in country coverage and variable availability, the project was narrowed to a focused question: how do wind and solar capacity expansions relate to renewable electricity generation and renewable electricity share across countries, and do those effects appear with a lag?

The final analysis uses a sequence of methods that move from data preparation to descriptive exploration, baseline regression, lagged-capacity modeling, and a supporting decomposition of renewable electricity share. This structure was chosen because it provides a clear progression. First, the data had to be merged and filtered into usable panels. Second, exploratory analysis was needed to understand broad patterns in renewable energy adoption across countries. Third, fixed-effects regression models were used to estimate the relationship between installed capacity and renewable generation while controlling for country-specific and year-specific differences. Finally, lagged-capacity models were added to test whether installed capacity has a delayed relationship with generation and renewable share. A renewable-share decomposition was also used to explain whether wind, solar, hydro, or other renewable sources were responsible for changes in each country's renewable electricity mix.

## Data Sources and Preparation

The project began with 17 raw CSV files related to renewable energy. These files included indicators such as renewable share of energy, renewable electricity generation, hydropower consumption, wind generation, installed wind capacity, solar generation, installed solar capacity, biofuel production, and geothermal capacity. The raw files are stored in `data/raw_renewables/`. Because each source file contained different variables and did not always include the same countries or years, the first major task was data preparation.

The merging process is documented in `focused_renewables_analysis/notebooks/merging_data_notebook.ipynb`. The notebook loads the raw CSV files, stores them as pandas DataFrames, and compares country coverage across datasets. This step was important because the project could not assume that every country appeared in every file. Some datasets had broad coverage, while others, especially installed capacity datasets, were available for a smaller set of countries. The notebook therefore checks which countries are missing from each dataset and identifies which files provide the most complete overlap for modeling.

From this process, three derived datasets were created and stored in `data/derived_renewables/`. The broadest file, `merged_renewables_data.csv`, contains 8,851 rows and 11 columns across 251 entities. This dataset includes renewable generation and electricity-share variables, such as electricity from wind, hydro, and solar, along with renewables as a percentage of electricity. A smaller file, `merged_capacity_data.csv`, contains 684 rows and 12 columns across 12 entities. This file includes installed wind and solar capacity, along with generation variables from wind, solar, and hydro. A third file, `six_country_merged_data.csv`, combines a wider set of variables for a small set of countries with more complete overlap.

For the focused analysis, the most important merge combines the capacity data with the renewable electricity share data. Aggregate regions, such as Africa and income-group categories, were removed from the modeling sample because the main regression models were designed to compare countries rather than mixed regional or economic groupings. After this filtering, the key capacity-based regression sample includes 9 countries and covers the years where wind and solar capacity data are available. The focus on this smaller sample is a limitation, but it allows the project to use comparable capacity, generation, and electricity-share variables in the same models.

## Exploratory Data Analysis

The exploratory data analysis was designed to understand renewable electricity patterns before fitting statistical models. This work is mainly contained in `focused_renewables_analysis/notebooks/regression_analysis.ipynb`. The EDA examines wind and solar capacity over time, wind and solar generation over time, and scatterplots of installed capacity versus electricity generation. These visuals help show whether the main regression relationships are plausible before estimating formal models.

One reason EDA matters in this project is that countries differ greatly in scale. Large countries such as China and the United States have much higher absolute levels of generation and capacity than smaller countries. If the analysis only used pooled raw data without accounting for country differences, the largest countries would dominate the results. The EDA therefore motivates the use of country fixed effects in the regression models. Country fixed effects help control for stable differences across countries, such as size, geography, industrial structure, and baseline electricity demand.

The exploratory plots also help show technology timing. Wind capacity appears earlier in the sample for many countries, while solar capacity tends to accelerate later, especially after the 2000s. This pattern matters because the relationship between capacity and generation may not be fully immediate. A solar or wind project added in one year may show its full production effects later, depending on construction timing, grid integration, reporting conventions, and utilization. These observations led to the later use of lagged-capacity models.

In addition to time-series plots, the EDA includes pooled scatterplots of capacity versus generation. These plots show a strong positive relationship between installed capacity and generation for both wind and solar. The scatterplots are not treated as causal evidence, but they provide a visual foundation for the regression analysis. They show that countries and years with more installed capacity generally have more electricity generation from that source.

## Baseline Fixed-Effects Regression Models

The main statistical method used in the focused analysis is fixed-effects regression. The baseline models ask whether installed wind capacity predicts wind generation and whether installed solar capacity predicts solar generation. A second set of models asks whether wind and solar capacity predict renewable electricity share. The basic purpose of these models is to estimate the relationship between capacity and outcomes while controlling for country and year effects.

The generation models can be written conceptually as:

```text
Generation_it = beta * Capacity_it + Country Fixed Effects + Year Fixed Effects + error_it
```

In this setup, `i` represents the country and `t` represents the year. The dependent variable is either wind generation or solar generation. The main independent variable is the corresponding installed capacity measure. Country fixed effects control for time-invariant country characteristics, while year fixed effects control for global shocks or trends that affect all countries in a given year. For example, year effects help account for broad changes in technology costs, global policy attention, or reporting patterns.

The baseline regression results show strong relationships between capacity and generation. In the contemporaneous wind model, an additional gigawatt of wind capacity is associated with approximately 1.95 additional terawatt-hours of wind generation, with an R-squared of about 0.97. In the solar model, an additional gigawatt of solar capacity is associated with approximately 1.06 additional terawatt-hours of solar generation, also with an R-squared of about 0.97. These high model fits are not surprising because installed capacity and generation are mechanically related: more installed capacity generally allows more electricity to be generated.

The renewable electricity share model is more difficult. In that model, the dependent variable is renewables as a percentage of electricity, and the predictors are wind capacity and solar capacity. This model asks a broader question: does installing more wind or solar capacity change the overall electricity mix? The coefficients in the renewable-share model are weaker and not statistically strong in the same way as the generation models. This makes sense because renewable electricity share depends on more than wind and solar capacity alone. It also depends on hydroelectric output, fossil fuel generation, electricity demand, policy, storage, grid infrastructure, and other sources of renewable energy.

## Lagged Capacity Models

The main extension beyond the baseline regressions is the lagged-capacity analysis, implemented in `focused_renewables_analysis/scripts/renewables_decomposition_lagged.py`. This analysis compares contemporaneous capacity models with models using one-year, two-year, and three-year lags of wind and solar capacity. The goal is to test whether capacity additions are associated with generation or renewable share after a delay.

For wind generation, the lagged models estimate relationships such as:

```text
Wind Generation_it = beta * Wind Capacity_i,t-lag + Country Fixed Effects + Year Fixed Effects + error_it
```

The same approach is used for solar generation and for renewable electricity share. The script creates lagged capacity variables within each country, so a one-year lag means that the model uses the previous year's installed capacity to predict the current year's outcome. This is repeated for lags of one, two, and three years.

The lagged results strengthen the timing story for generation. For wind generation, the coefficient rises from about 1.95 with no lag to about 2.32 with a one-year lag, 2.75 with a two-year lag, and 3.09 with a three-year lag. For solar generation, the coefficient rises from about 1.06 with no lag to about 1.30 with a one-year lag, 1.58 with a two-year lag, and 1.91 with a three-year lag. These results suggest that installed capacity remains strongly associated with later generation. The increasing coefficients are consistent with the idea that capacity investments may take time to appear fully in generation outcomes.

However, these lagged models should not be interpreted as definitive causal estimates. They improve the timing structure compared with purely contemporaneous models, but they still rely on observational data. Countries that add renewable capacity may also be changing policies, electricity demand, grid infrastructure, or fossil fuel generation at the same time. The lagged models show association with timing, not a fully isolated causal effect.

For renewable electricity share, lagged capacity is still weaker. Wind and solar capacity lags do not become clearly significant predictors of total renewable share in the joint model. This suggests that the relationship between capacity and generation is much more direct than the relationship between capacity and the overall electricity mix. In other words, new wind and solar capacity can increase wind and solar generation, but whether that changes the total renewable share depends on what is happening to the rest of the electricity system.

## Renewable-Share Decomposition

The final supporting method is renewable-share decomposition. This analysis asks which renewable source explains the change in renewable electricity share for each country. Instead of modeling the relationship statistically, the decomposition compares the first and last available years for each country and calculates the change in wind share, solar share, hydro share, and other renewable share.

The decomposition is useful because renewable electricity share can rise or fall for different reasons. In Denmark, for example, renewable electricity share increased sharply between 1985 and 2021, and most of that increase came from wind. In Germany, wind also explains a large portion of the increase, with solar contributing as a secondary driver. Japan looks more solar-driven. In contrast, countries such as Mexico, India, and Pakistan show declining total renewable electricity share over the period because hydro's share fell more than wind and solar increased.

This decomposition helps explain why the renewable-share regression is more complicated than the generation regression. Wind and solar capacity may increase, but total renewable share can still be affected by falling hydro share, rising electricity demand, or changes in nonrenewable generation. The decomposition therefore provides context for interpreting the weaker renewable-share regression results.

## Limitations

The most important limitation is sample size. The broad renewables panel covers 251 entities, but installed wind and solar capacity data are available for a much smaller set of countries. The deepest regression models therefore use only 9 countries. This makes the results useful for understanding those countries but limits generalizability.

A second limitation is that capacity and generation are physically related. The generation regressions are useful because they confirm the expected relationship and show how it behaves with lags, but they should not be oversold as surprising causal findings. The renewable-share models are more policy-relevant but also harder to explain because they depend on broader electricity-system dynamics.

A third limitation is that the models do not include every important control variable. The current analysis does not directly control for electricity demand, fossil fuel generation, renewable policy, storage, transmission capacity, or energy prices. Adding such variables could improve the interpretation of the renewable-share models.

## Conclusion

The methods used in this project form a coherent workflow for studying renewable electricity growth. The project begins with data cleaning and merging, then uses exploratory analysis to understand major country and technology patterns. Baseline fixed-effects regressions estimate the relationship between installed capacity and generation or renewable share. Lagged-capacity models extend the analysis by testing whether capacity additions are associated with later production. Finally, renewable-share decomposition helps explain which sources drive changes in renewable electricity share by country.

Overall, the strongest methodological contribution is the lagged fixed-effects analysis. It connects the descriptive patterns in the data to a clearer modeling question: whether wind and solar capacity expansions are associated with later renewable generation. The results show that capacity strongly predicts generation, especially when lagged, but total renewable electricity share remains harder to explain because it depends on the broader electricity mix.
