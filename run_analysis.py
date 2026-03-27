"""
Afet analizi — Jupyter olmadan calistirmak icin.
Proje klasorunde: python run_analysis.py

Grafikler outputs/ altina yazilir.
"""
from __future__ import annotations

import folium
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data_loader import load_or_create_data, project_root
from src.risk_utils import compute_region_risk_scores

OUTPUT_DIR = project_root() / "outputs"


def main() -> None:
    data_dir = project_root() / "data"
    data_dir.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    sns.set(style="whitegrid")

    df = load_or_create_data()

    df["year"] = df["date"].dt.year
    events_per_year = (
        df.groupby(["year", "disaster_type"])["location"]
        .count()
        .reset_index(name="event_count")
    )
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=events_per_year,
        x="year",
        y="event_count",
        hue="disaster_type",
        marker="o",
    )
    plt.title("Yillara gore afet sikligi")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_frequency_by_year.png", dpi=150)
    plt.close()

    impact_by_region = (
        df.groupby("location")["affected_people"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    top_n = 10
    top_regions = impact_by_region.head(top_n)
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top_regions,
        x="affected_people",
        y="location",
        hue="location",
        palette="Reds_r",
        legend=False,
    )
    plt.title(f"Etkilenen kisi — ilk {top_n} bolge")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "02_top_regions.png", dpi=150)
    plt.close()

    sample = df.sample(min(400, len(df)), random_state=0)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=sample,
        x="magnitude",
        y="economic_damage",
        hue="disaster_type",
        alpha=0.7,
    )
    plt.yscale("log")
    plt.title("Buyukluk vs ekonomik zarar (log)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_magnitude_vs_damage.png", dpi=150)
    plt.close()

    region_risk = compute_region_risk_scores(df)
    region_risk.to_csv(OUTPUT_DIR / "region_risk_scores.csv", index=False)

    top_k = 10
    top_risk = region_risk.head(top_k).copy()
    m = folium.Map(location=[39.0, 35.2], zoom_start=6, tiles="cartodbpositron")
    rmin, rmax = top_risk["risk_score"].min(), top_risk["risk_score"].max()
    eps = 1e-9
    top_risk["risk_norm"] = (top_risk["risk_score"] - rmin) / (rmax - rmin + eps)

    for _, row in top_risk.iterrows():
        rn = row["risk_norm"]
        radius = 12000 + 38000 * rn
        color = "#ffcc00" if rn < 0.5 else "#ff3300"
        popup = (
            f"<b>{row['location']}</b><br>"
            f"Risk: {row['risk_score']:.2f}<br>"
            f"Olay: {int(row['event_count'])}"
        )
        folium.Circle(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=folium.Popup(popup, max_width=300),
        ).add_to(m)

    map_path = OUTPUT_DIR / "risk_map.html"
    m.save(str(map_path))

    corr = (
        df[["magnitude", "economic_damage"]]
        .assign(log_damage=np.log1p(df["economic_damage"]))
        .corr()
        .loc["magnitude", "log_damage"]
    )

    print("Bitti.")
    print(f"Kayit sayisi: {len(df)}")
    print(f"Buyukluk / log(zarar) korelasyonu: {corr:.2f}")
    print(f"Grafikler: {OUTPUT_DIR}")
    print(f"Haritayi tarayicida ac: {map_path}")


if __name__ == "__main__":
    main()
