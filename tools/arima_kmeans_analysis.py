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
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

RENEWABLES = ROOT / "merged_renewables_data.csv"
CAPACITY = ROOT / "merged_capacity_data.csv"

AGGREGATES = {
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "World",
    "European Union (27)",
    "European Union (28)",
    "European Union (27) countries",
    "Lower-middle-income countries",
    "Upper-middle-income countries",
    "High-income countries",
    "Low-income countries",
    "Middle-income countries",
    "OECD",
    "Non-OECD",
    "Upper-middle-income countries",
    "Lower-middle-income countries",
}


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
                    model = ARIMA(series, order=(p, d, q))
                    fitted = model.fit()
                    if np.isfinite(fitted.aic) and fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except Exception:
                    continue
    return best_order


def run_arima(country: str = "Denmark", value_col: str = "Renewables (% electricity)") -> pd.DataFrame:
    ren = pd.read_csv(RENEWABLES)
    country_df = (
        ren.loc[ren["Entity"] == country, ["Year", value_col]]
        .dropna()
        .sort_values("Year")
        .reset_index(drop=True)
    )
    if len(country_df) < 20:
        raise ValueError(f"Not enough data for ARIMA: {country} / {value_col}")

    periods = pd.PeriodIndex(country_df["Year"].astype(int), freq="Y")
    ts = pd.Series(country_df[value_col].to_numpy(), index=periods, name=value_col)

    test_horizon = 8
    train = ts.iloc[:-test_horizon]
    test = ts.iloc[-test_horizon:]
    order = choose_arima_order(train)

    model = ARIMA(train, order=order)
    fitted = model.fit()
    forecast_res = fitted.get_forecast(steps=test_horizon)
    forecast = pd.Series(forecast_res.predicted_mean.to_numpy(), index=test.index, name="forecast")
    conf = forecast_res.conf_int()

    metrics = {
        "country": country,
        "series": value_col,
        "order": str(order),
        "train_start": int(train.index.min().year),
        "train_end": int(train.index.max().year),
        "test_start": int(test.index.min().year),
        "test_end": int(test.index.max().year),
        "mae": float(np.mean(np.abs(test - forecast))),
        "rmse": float(np.sqrt(np.mean((test - forecast) ** 2))),
        "mape_percent": float(np.mean(np.abs((test - forecast) / test)) * 100),
        "aic": float(fitted.aic),
    }
    pd.DataFrame([metrics]).to_csv(OUT / "arima_metrics.csv", index=False)

    forecast_df = pd.DataFrame(
        {
            "Year": test.index.astype(str),
            "actual": test.to_numpy(),
            "forecast": forecast.to_numpy(),
            "lower_ci": conf.iloc[:, 0].to_numpy(),
            "upper_ci": conf.iloc[:, 1].to_numpy(),
        }
    )
    forecast_df.to_csv(OUT / "arima_forecast.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(ts.index.year, ts.values, label="Observed", linewidth=2, color="#1f4e79")
    plt.plot(forecast.index.year, forecast.values, label="Forecast", linewidth=2, linestyle="--", color="#c55a11")
    plt.fill_between(
        forecast.index.year,
        conf.iloc[:, 0].to_numpy(),
        conf.iloc[:, 1].to_numpy(),
        color="#f4b183",
        alpha=0.35,
        label="95% CI",
    )
    plt.axvline(test.index.min().year, color="gray", linestyle=":", linewidth=1.2, label="Test period")
    plt.title(f"ARIMA Forecast: {country} {value_col}")
    plt.xlabel("Year")
    plt.ylabel(value_col)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "arima_forecast.png", dpi=200)
    plt.close()

    return pd.DataFrame([metrics])


def annual_slope(group: pd.DataFrame, value_col: str) -> float:
    x = group["Year"].to_numpy(dtype=float)
    y = group[value_col].to_numpy(dtype=float)
    if len(np.unique(x)) < 2:
        return np.nan
    return float(np.polyfit(x, y, 1)[0])


def run_kmeans(n_clusters: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    ren = pd.read_csv(RENEWABLES)
    ren = ren[~ren["Entity"].isin(AGGREGATES)].copy()
    ren = ren[ren["Code"].notna()].copy()

    recent = ren[(ren["Year"] >= 2010) & (ren["Year"] <= 2022)].copy()
    recent = recent.dropna(
        subset=[
            "Renewables (% electricity)",
            "Wind (% electricity)",
            "Solar (% electricity)",
            "Hydro (% electricity)",
        ]
    )

    counts = recent.groupby("Entity")["Year"].count()
    keep = counts[counts >= 10].index
    recent = recent[recent["Entity"].isin(keep)].copy()

    recent_subset = recent[
        [
            "Entity",
            "Year",
            "Renewables (% electricity)",
            "Wind (% electricity)",
            "Solar (% electricity)",
            "Hydro (% electricity)",
        ]
    ].copy()

    features = recent_subset.groupby("Entity").apply(
        lambda g: pd.Series(
            {
                "avg_renew_share": g["Renewables (% electricity)"].mean(),
                "latest_renew_share": g.sort_values("Year")["Renewables (% electricity)"].iloc[-1],
                "renew_share_growth": annual_slope(g, "Renewables (% electricity)"),
                "avg_wind_share": g["Wind (% electricity)"].mean(),
                "avg_solar_share": g["Solar (% electricity)"].mean(),
                "avg_hydro_share": g["Hydro (% electricity)"].mean(),
                "renew_share_sd": g["Renewables (% electricity)"].std(),
            }
        ),
        include_groups=False,
    ).dropna()
    features = features.reset_index()

    feature_cols = [c for c in features.columns if c != "Entity"]
    scaler = StandardScaler()
    X = scaler.fit_transform(features[feature_cols])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = kmeans.fit_predict(X)
    features["cluster"] = labels

    silhouette = silhouette_score(X, labels)
    pd.DataFrame([{"n_clusters": n_clusters, "silhouette_score": float(silhouette)}]).to_csv(
        OUT / "kmeans_metrics.csv", index=False
    )

    cluster_summary = (
        features.groupby("cluster")
        .agg(
            countries=("Entity", "count"),
            avg_renew_share=("avg_renew_share", "mean"),
            latest_renew_share=("latest_renew_share", "mean"),
            renew_share_growth=("renew_share_growth", "mean"),
            avg_wind_share=("avg_wind_share", "mean"),
            avg_solar_share=("avg_solar_share", "mean"),
            avg_hydro_share=("avg_hydro_share", "mean"),
        )
        .round(2)
        .reset_index()
    )

    features.sort_values(["cluster", "Entity"]).to_csv(OUT / "kmeans_country_clusters.csv", index=False)
    cluster_summary.to_csv(OUT / "kmeans_cluster_summary.csv", index=False)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    loadings = pd.DataFrame(
        pca.components_.T,
        index=feature_cols,
        columns=["PC1", "PC2"],
    )
    loadings.to_csv(OUT / "kmeans_pca_loadings.csv")
    plot_df = features.copy()
    plot_df["pc1"] = coords[:, 0]
    plot_df["pc2"] = coords[:, 1]

    def pc_label(pc_name: str) -> str:
        series = loadings[pc_name].sort_values(key=lambda s: s.abs(), ascending=False).head(2)
        parts = []
        for idx, val in series.items():
            direction = "+" if val >= 0 else "-"
            parts.append(f"{direction}{idx}")
        explained = pca.explained_variance_ratio_[0 if pc_name == "PC1" else 1] * 100
        return f"{pc_name} ({explained:.1f}% var): " + ", ".join(parts)

    plt.figure(figsize=(9, 6))
    cmap = plt.get_cmap("tab10")
    for cluster in sorted(plot_df["cluster"].unique()):
        sub = plot_df[plot_df["cluster"] == cluster]
        plt.scatter(sub["pc1"], sub["pc2"], s=40, label=f"Cluster {cluster}", color=cmap(cluster))

    # Label a small set of higher-signal points to keep the plot readable.
    for _, row in plot_df.nlargest(15, "latest_renew_share").iterrows():
        plt.text(row["pc1"] + 0.03, row["pc2"] + 0.03, row["Entity"], fontsize=7)

    plt.title("K-means Clusters of Countries by Renewable Electricity Profile")
    plt.xlabel(pc_label("PC1"))
    plt.ylabel(pc_label("PC2"))
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "kmeans_clusters_pca.png", dpi=200)
    plt.close()

    return features, cluster_summary


def save_method_notes() -> None:
    notes = """ARIMA analysis
- Series: Denmark, Renewables (% electricity)
- Train/test split: hold out the final 8 annual observations
- Model selection: lowest AIC over ARIMA(p,d,q), p/d/q in {0,1,2}

K-means analysis
- Dataset: merged_renewables_data.csv
- Sample: entities with at least 10 non-missing annual observations from 2010-2022
- Features: renewable share level, latest share, linear growth, wind/solar/hydro average shares, and variability
- Standardization: z-score scaling before clustering
- Clusters: k=3
"""
    (OUT / "analysis_notes.txt").write_text(notes)


def main() -> None:
    arima_metrics = run_arima()
    _, cluster_summary = run_kmeans()
    save_method_notes()

    print("Saved outputs to", OUT)
    print("\nARIMA metrics")
    print(arima_metrics.to_string(index=False))
    print("\nCluster summary")
    print(cluster_summary.to_string(index=False))


if __name__ == "__main__":
    main()
