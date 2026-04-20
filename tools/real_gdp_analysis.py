from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA


ROOT = Path("/Users/jakeschwartz/642-Project")
DATA = ROOT / "real_gdp_data_six_countries.csv"
OUT = ROOT / "outputs" / "real_gdp"
OUT.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df = df.sort_values(["Country Name", "Year"]).reset_index(drop=True)
    df["log_gdp"] = np.log(df["Real GDP (2015 $)"])
    df["gdp_growth_pct"] = (
        df.groupby("Country Name")["Real GDP (2015 $)"].pct_change(fill_method=None) * 100
    )
    return df


def save_growth_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Country Name")
        .agg(
            start_year=("Year", "min"),
            end_year=("Year", "max"),
            latest_gdp=("Real GDP (2015 $)", "last"),
            mean_growth_pct=("gdp_growth_pct", "mean"),
            median_growth_pct=("gdp_growth_pct", "median"),
            growth_volatility=("gdp_growth_pct", "std"),
            min_growth_pct=("gdp_growth_pct", "min"),
            max_growth_pct=("gdp_growth_pct", "max"),
        )
        .round(3)
        .reset_index()
    )
    summary.to_csv(OUT / "gdp_growth_summary.csv", index=False)
    return summary


def save_period_growth(df: pd.DataFrame) -> pd.DataFrame:
    def period_label(year: int) -> str:
        if year <= 1989:
            return "1960-1989"
        if year <= 2007:
            return "1990-2007"
        if year <= 2019:
            return "2008-2019"
        return "2020-2025"

    period_df = df.dropna(subset=["gdp_growth_pct"]).copy()
    period_df["period"] = period_df["Year"].map(period_label)
    out = (
        period_df.groupby(["Country Name", "period"])["gdp_growth_pct"]
        .mean()
        .round(3)
        .reset_index()
        .pivot(index="Country Name", columns="period", values="gdp_growth_pct")
        .reset_index()
    )
    out.to_csv(OUT / "gdp_growth_by_period.csv", index=False)
    return out


def plot_series(df: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 6))
    for country, sub in df.groupby("Country Name"):
        plt.plot(sub["Year"], sub["Real GDP (2015 $)"], linewidth=2, label=country)
    plt.title("Real GDP by Country")
    plt.xlabel("Year")
    plt.ylabel("Real GDP (2015 $)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "real_gdp_levels.png", dpi=200)
    plt.close()

    plt.figure(figsize=(11, 6))
    for country, sub in df.groupby("Country Name"):
        plt.plot(sub["Year"], sub["log_gdp"], linewidth=2, label=country)
    plt.title("Log Real GDP by Country")
    plt.xlabel("Year")
    plt.ylabel("log(Real GDP)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "real_gdp_log_levels.png", dpi=200)
    plt.close()

    plt.figure(figsize=(11, 6))
    for country, sub in df.groupby("Country Name"):
        plt.plot(sub["Year"], sub["gdp_growth_pct"], linewidth=1.6, label=country)
    for shock_year in [1973, 2008, 2020]:
        plt.axvline(shock_year, color="gray", linestyle=":", linewidth=1)
    plt.title("Annual Real GDP Growth by Country")
    plt.xlabel("Year")
    plt.ylabel("Growth Rate (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "real_gdp_growth_rates.png", dpi=200)
    plt.close()


def choose_arima_order(
    series: pd.Series,
    p_values: Iterable[int] = range(0, 3),
    d_values: Iterable[int] = range(0, 3),
    q_values: Iterable[int] = range(0, 3),
) -> tuple[int, int, int]:
    best_order = (1, 1, 0)
    best_aic = np.inf
    for p in p_values:
        for d in d_values:
            for q in q_values:
                try:
                    fitted = ARIMA(series, order=(p, d, q)).fit()
                    if np.isfinite(fitted.aic) and fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except Exception:
                    continue
    return best_order


def run_arima(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    plt.figure(figsize=(12, 7))

    for country, sub in df.groupby("Country Name"):
        sub = sub.sort_values("Year").copy()
        periods = pd.PeriodIndex(sub["Year"].astype(int), freq="Y")
        ts = pd.Series(sub["log_gdp"].to_numpy(), index=periods, name="log_gdp")

        test_horizon = 6
        train = ts.iloc[:-test_horizon]
        test = ts.iloc[-test_horizon:]
        order = choose_arima_order(train)
        fitted = ARIMA(train, order=order).fit()
        forecast = fitted.get_forecast(steps=test_horizon).predicted_mean

        rows.append(
            {
                "Country Name": country,
                "order": str(order),
                "train_end": int(train.index.max().year),
                "test_start": int(test.index.min().year),
                "test_end": int(test.index.max().year),
                "mae_log_gdp": float(np.mean(np.abs(test - forecast))),
                "rmse_log_gdp": float(np.sqrt(np.mean((test - forecast) ** 2))),
                "aic": float(fitted.aic),
            }
        )

        plt.plot(test.index.year, test.values, linewidth=2, label=f"{country} actual")
        plt.plot(test.index.year, forecast.values, linestyle="--", linewidth=2, label=f"{country} forecast")

    metrics = pd.DataFrame(rows).sort_values("Country Name").reset_index(drop=True)
    metrics.to_csv(OUT / "arima_country_metrics.csv", index=False)

    plt.title("ARIMA Forecasts on log(Real GDP): Last 6 Years by Country")
    plt.xlabel("Year")
    plt.ylabel("log(Real GDP)")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "arima_country_forecasts.png", dpi=200)
    plt.close()

    return metrics


def run_kmeans(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    growth = df.dropna(subset=["gdp_growth_pct"]).copy()
    features = []

    for country, sub in growth.groupby("Country Name"):
        sub = sub.sort_values("Year")
        pre_2000 = sub[sub["Year"] <= 1999]["gdp_growth_pct"]
        post_2000 = sub[sub["Year"] >= 2000]["gdp_growth_pct"]
        crisis_2008 = sub[sub["Year"].between(2008, 2009)]["gdp_growth_pct"]
        covid = sub[sub["Year"].between(2020, 2021)]["gdp_growth_pct"]
        X = sub["Year"].to_numpy(dtype=float)
        y = sub["gdp_growth_pct"].to_numpy(dtype=float)
        trend = float(np.polyfit(X, y, 1)[0]) if len(np.unique(X)) > 1 else np.nan

        features.append(
            {
                "Country Name": country,
                "latest_log_gdp": float(sub["log_gdp"].iloc[-1]),
                "mean_growth_pct": float(sub["gdp_growth_pct"].mean()),
                "growth_volatility": float(sub["gdp_growth_pct"].std()),
                "pre_2000_growth": float(pre_2000.mean()) if len(pre_2000) else np.nan,
                "post_2000_growth": float(post_2000.mean()) if len(post_2000) else np.nan,
                "crisis_2008_growth": float(crisis_2008.mean()) if len(crisis_2008) else np.nan,
                "covid_period_growth": float(covid.mean()) if len(covid) else np.nan,
                "growth_trend": trend,
            }
        )

    feature_df = pd.DataFrame(features)
    numeric_cols = [c for c in feature_df.columns if c != "Country Name"]
    feature_df[numeric_cols] = feature_df[numeric_cols].apply(lambda col: col.fillna(col.mean()))
    scaler = StandardScaler()
    X = scaler.fit_transform(feature_df[numeric_cols])

    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    feature_df["cluster"] = kmeans.fit_predict(X)

    metrics = pd.DataFrame(
        [{"n_clusters": n_clusters, "silhouette_score": float(silhouette_score(X, feature_df["cluster"]))}]
    )
    metrics.to_csv(OUT / "kmeans_metrics.csv", index=False)

    summary = (
        feature_df.groupby("cluster")
        .agg(
            countries=("Country Name", lambda x: ", ".join(sorted(x))),
            mean_growth_pct=("mean_growth_pct", "mean"),
            growth_volatility=("growth_volatility", "mean"),
            latest_log_gdp=("latest_log_gdp", "mean"),
            post_2000_growth=("post_2000_growth", "mean"),
        )
        .round(3)
        .reset_index()
    )

    feature_df.to_csv(OUT / "kmeans_country_clusters.csv", index=False)
    summary.to_csv(OUT / "kmeans_cluster_summary.csv", index=False)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    plot_df = feature_df.copy()
    plot_df["pc1"] = coords[:, 0]
    plot_df["pc2"] = coords[:, 1]

    plt.figure(figsize=(8, 6))
    cmap = plt.get_cmap("tab10")
    for cluster in sorted(plot_df["cluster"].unique()):
        sub = plot_df[plot_df["cluster"] == cluster]
        plt.scatter(sub["pc1"], sub["pc2"], s=70, color=cmap(cluster), label=f"Cluster {cluster}")
        for _, row in sub.iterrows():
            plt.text(row["pc1"] + 0.03, row["pc2"] + 0.03, row["Country Name"], fontsize=8)
    plt.title("K-means Clusters of Countries by GDP Growth Profile")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "kmeans_gdp_clusters.png", dpi=200)
    plt.close()

    return feature_df, summary


def write_notes() -> None:
    notes = """What each analysis does
- EDA: shows level differences, growth patterns, and major shocks.
- ARIMA: forecasts each country's log real GDP using only its own past values.
- K-means: groups countries with similar GDP growth profiles based on summary features.

Interpretation guidance
- ARIMA is useful for short-run forecasting, not causal explanation.
- K-means is exploratory and descriptive, especially with only six countries.
- Growth-rate plots and period averages often tell the clearest substantive story.
"""
    (OUT / "analysis_notes.txt").write_text(notes)


def main() -> None:
    df = load_data()
    growth_summary = save_growth_summary(df)
    period_growth = save_period_growth(df)
    plot_series(df)
    arima_metrics = run_arima(df)
    _, cluster_summary = run_kmeans(df)
    write_notes()

    print("Saved outputs to", OUT)
    print("\nGrowth summary")
    print(growth_summary.to_string(index=False))
    print("\nPeriod growth")
    print(period_growth.to_string(index=False))
    print("\nARIMA metrics")
    print(arima_metrics.to_string(index=False))
    print("\nCluster summary")
    print(cluster_summary.to_string(index=False))


if __name__ == "__main__":
    main()
