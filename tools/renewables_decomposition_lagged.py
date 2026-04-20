from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path("/Users/jakeschwartz/642-Project")
OUT = ROOT / "outputs" / "renewables_extensions"
OUT.mkdir(parents=True, exist_ok=True)

RENEWABLES = ROOT / "merged_renewables_data.csv"
CAPACITY = ROOT / "merged_capacity_data.csv"

AGGREGATES = {
    "Africa",
    "Lower-middle-income countries",
    "Upper-middle-income countries",
}


def load_panel() -> pd.DataFrame:
    ren = pd.read_csv(RENEWABLES)
    cap = pd.read_csv(CAPACITY)
    df = cap.merge(
        ren[
            [
                "Entity",
                "Year",
                "Renewables (% electricity)",
                "Hydro (% electricity)",
                "Wind (% electricity)",
                "Solar (% electricity)",
                "Electricity from wind (TWh)",
                "Electricity from solar (TWh)",
                "Electricity from hydro (TWh)",
            ]
        ],
        on=["Entity", "Year"],
        how="inner",
    )
    df = df[~df["Entity"].isin(AGGREGATES)].copy()
    df = df.rename(
        columns={
            "Wind Capacity": "wind_cap",
            "Solar Capacity": "solar_cap",
            "Wind Generation - TWh": "wind_gen_capfile",
            "Solar Generation - TWh": "solar_gen_capfile",
            "Hydro Generation - TWh": "hydro_gen_capfile",
            "Renewables (% electricity)": "renew_share_elec",
            "Hydro (% electricity)": "hydro_share_elec",
            "Wind (% electricity)": "wind_share_elec",
            "Solar (% electricity)": "solar_share_elec",
            "Electricity from wind (TWh)": "wind_gen",
            "Electricity from solar (TWh)": "solar_gen",
            "Electricity from hydro (TWh)": "hydro_gen",
        }
    )
    return df.sort_values(["Entity", "Year"]).reset_index(drop=True)


def growth_decomposition(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []

    for country, sub in df.groupby("Entity"):
        sub = sub.dropna(
            subset=["renew_share_elec", "wind_share_elec", "solar_share_elec", "hydro_share_elec"]
        ).sort_values("Year")
        if len(sub) < 2:
            continue

        first = sub.iloc[0]
        last = sub.iloc[-1]
        delta_total = float(last["renew_share_elec"] - first["renew_share_elec"])
        delta_wind = float(last["wind_share_elec"] - first["wind_share_elec"])
        delta_solar = float(last["solar_share_elec"] - first["solar_share_elec"])
        delta_hydro = float(last["hydro_share_elec"] - first["hydro_share_elec"])
        delta_other = delta_total - (delta_wind + delta_solar + delta_hydro)

        if abs(delta_total) > 1e-9:
            wind_contrib = 100 * delta_wind / delta_total
            solar_contrib = 100 * delta_solar / delta_total
            hydro_contrib = 100 * delta_hydro / delta_total
            other_contrib = 100 * delta_other / delta_total
        else:
            wind_contrib = solar_contrib = hydro_contrib = other_contrib = np.nan

        rows.append(
            {
                "Entity": country,
                "start_year": int(first["Year"]),
                "end_year": int(last["Year"]),
                "renew_share_change_pp": round(delta_total, 3),
                "wind_share_change_pp": round(delta_wind, 3),
                "solar_share_change_pp": round(delta_solar, 3),
                "hydro_share_change_pp": round(delta_hydro, 3),
                "other_share_change_pp": round(delta_other, 3),
                "wind_contribution_pct": round(wind_contrib, 2),
                "solar_contribution_pct": round(solar_contrib, 2),
                "hydro_contribution_pct": round(hydro_contrib, 2),
                "other_contribution_pct": round(other_contrib, 2),
            }
        )

    out = pd.DataFrame(rows).sort_values("renew_share_change_pp", ascending=False).reset_index(drop=True)
    out.to_csv(OUT / "renewable_share_decomposition.csv", index=False)

    plot_df = out.sort_values("renew_share_change_pp")
    y = np.arange(len(plot_df))
    plt.figure(figsize=(10, 7))
    left = np.zeros(len(plot_df))
    for col, color, label in [
        ("hydro_share_change_pp", "#4f81bd", "Hydro"),
        ("wind_share_change_pp", "#9bbb59", "Wind"),
        ("solar_share_change_pp", "#f79646", "Solar"),
        ("other_share_change_pp", "#7f7f7f", "Other"),
    ]:
        vals = plot_df[col].to_numpy()
        plt.barh(plot_df["Entity"], vals, left=left, color=color, label=label)
        left = left + vals
    plt.axvline(0, color="black", linewidth=0.8)
    plt.title("Change in Renewable Electricity Share by Source")
    plt.xlabel("Percentage-point change from first to last available year")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "renewable_share_decomposition.png", dpi=200)
    plt.close()

    return out


def add_lags(df: pd.DataFrame, max_lag: int = 3) -> pd.DataFrame:
    out = df.copy()
    for lag in range(1, max_lag + 1):
        out[f"wind_cap_lag{lag}"] = out.groupby("Entity")["wind_cap"].shift(lag)
        out[f"solar_cap_lag{lag}"] = out.groupby("Entity")["solar_cap"].shift(lag)
    return out


def fit_lag_models(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []
    max_lag = 3
    panel = add_lags(df, max_lag=max_lag)

    specs = [
        ("wind_gen", "wind capacity -> wind generation", "wind"),
        ("solar_gen", "solar capacity -> solar generation", "solar"),
        ("renew_share_elec", "capacity -> renewable electricity share", "both"),
    ]

    for outcome, label, predictor_type in specs:
        for lag in range(0, max_lag + 1):
            if predictor_type == "wind":
                rhs = "wind_cap" if lag == 0 else f"wind_cap_lag{lag}"
                needed = [outcome, rhs]
                formula = f"{outcome} ~ {rhs} + C(Entity) + C(Year)"
                coef_names = [rhs]
            elif predictor_type == "solar":
                rhs = "solar_cap" if lag == 0 else f"solar_cap_lag{lag}"
                needed = [outcome, rhs]
                formula = f"{outcome} ~ {rhs} + C(Entity) + C(Year)"
                coef_names = [rhs]
            else:
                wind_rhs = "wind_cap" if lag == 0 else f"wind_cap_lag{lag}"
                solar_rhs = "solar_cap" if lag == 0 else f"solar_cap_lag{lag}"
                needed = [outcome, wind_rhs, solar_rhs]
                formula = f"{outcome} ~ {wind_rhs} + {solar_rhs} + C(Entity) + C(Year)"
                coef_names = [wind_rhs, solar_rhs]

            reg_df = panel.dropna(subset=needed).copy()
            if len(reg_df) == 0:
                continue

            model = smf.ols(formula, data=reg_df).fit(cov_type="HC3")
            table = model.summary2().tables[1]
            for coef_name in coef_names:
                row = table.loc[coef_name]
                pcol = "P>|z|" if "P>|z|" in row.index else "P>|t|"
                rows.append(
                    {
                        "model": label,
                        "outcome": outcome,
                        "lag_years": lag,
                        "predictor": coef_name,
                        "coef": float(row["Coef."]),
                        "std_err": float(row["Std.Err."]),
                        "p_value": float(row[pcol]),
                        "r_squared": float(model.rsquared),
                        "n_obs": int(model.nobs),
                    }
                )

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "lagged_capacity_models.csv", index=False)

    for outcome in ["wind_gen", "solar_gen", "renew_share_elec"]:
        sub = out[out["outcome"] == outcome].copy()
        if sub.empty:
            continue
        plt.figure(figsize=(8, 5))
        for predictor, color in zip(sub["predictor"].unique(), ["#9bbb59", "#f79646"]):
            psub = sub[sub["predictor"] == predictor]
            plt.plot(psub["lag_years"], psub["coef"], marker="o", linewidth=2, label=predictor, color=color)
        plt.axhline(0, color="black", linewidth=0.8)
        plt.xticks(sorted(sub["lag_years"].unique()))
        plt.title(f"Lagged Capacity Coefficients: {outcome}")
        plt.xlabel("Lag in years")
        plt.ylabel("Coefficient")
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT / f"lagged_capacity_{outcome}.png", dpi=200)
        plt.close()

    return out


def save_notes() -> None:
    notes = """Growth decomposition
- Measures the total change in renewable electricity share for each country.
- Splits that change into wind, solar, hydro, and residual 'other' components.
- Useful for saying which source explains the rise in renewable electricity share.

Lagged capacity models
- Fixed-effects regressions with country and year controls.
- Compare contemporaneous, 1-year, 2-year, and 3-year lags of wind/solar capacity.
- Useful for checking whether capacity additions show up later in generation or renewable share.
"""
    (OUT / "analysis_notes.txt").write_text(notes)


def main() -> None:
    df = load_panel()
    decomp = growth_decomposition(df)
    lagged = fit_lag_models(df)
    save_notes()

    print("Saved outputs to", OUT)
    print("\nDecomposition")
    print(decomp.to_string(index=False))
    print("\nLagged models")
    print(lagged.to_string(index=False))


if __name__ == "__main__":
    main()
