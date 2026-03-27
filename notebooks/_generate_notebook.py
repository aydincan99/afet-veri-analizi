"""One-off script: writes disaster_analysis.ipynb as valid nbformat JSON."""
from __future__ import annotations

import json
from pathlib import Path


def lines(s: str) -> list[str]:
    if s and not s.endswith("\n"):
        s += "\n"
    return s.splitlines(keepends=True)


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": lines(text)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines(text),
    }


NOTEBOOK = {
    "cells": [
        md(
            """# Afet verisi analizi: deprem ve sel

Bu not defteri, sentetik afet verisiyle **hangi bölgelerin daha riskli** olduğunu ve **zaman içinde sıklığı** göstermek için hazırlanmıştır; insani yardım kararlarına destek olması amaçlanır.

- Sentetik veri seti oluşturma veya yükleme
- En çok etkilenen bölgeler ve yıllara göre sıklık
- Büyüklük ve ekonomik zarar ilişkisi
- Basit risk skoru ve harita görselleştirmesi
"""
        ),
        code(
            """# Gerekli kütüphaneler ve proje yolu (Jupyter notebooks/ klasöründen çalışır)
import sys
from pathlib import Path

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Proje kökünü Python yoluna ekle (src.risk_utils içe aktarımı için)
PROJECT_ROOT = Path("..").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.risk_utils import compute_region_risk_scores

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

data_dir = PROJECT_ROOT / "data"
data_dir.mkdir(exist_ok=True)
"""
        ),
        md(
            """## 1. Veri seti: oluştur veya yükle

Sütunlar: `location`, `disaster_type`, `magnitude`, `date`, `affected_people`, `economic_damage`, `latitude`, `longitude`.
"""
        ),
        code(
            """csv_path = data_dir / "disaster_data.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path, parse_dates=["date"])
else:
    rng = np.random.default_rng(seed=42)
    locations = [
        ("Istanbul, Turkey", 41.0082, 28.9784),
        ("Izmir, Turkey", 38.4237, 27.1428),
        ("Tokyo, Japan", 35.6762, 139.6503),
        ("Osaka, Japan", 34.6937, 135.5023),
        ("Jakarta, Indonesia", -6.2088, 106.8456),
        ("Manila, Philippines", 14.5995, 120.9842),
        ("Los Angeles, USA", 34.0522, -118.2437),
        ("San Francisco, USA", 37.7749, -122.4194),
        ("Lima, Peru", -12.0464, -77.0428),
        ("Dhaka, Bangladesh", 23.8103, 90.4125),
    ]
    disaster_types = ["earthquake", "flood"]
    n_events = 800
    loc_indices = rng.integers(0, len(locations), size=n_events)
    chosen_locs = [locations[i] for i in loc_indices]
    location_names = [loc[0] for loc in chosen_locs]
    latitudes = [loc[1] for loc in chosen_locs]
    longitudes = [loc[2] for loc in chosen_locs]
    disaster_choices = rng.choice(disaster_types, size=n_events, p=[0.5, 0.5])
    start_date = pd.Timestamp("2000-01-01")
    end_date = pd.Timestamp("2025-12-31")
    total_days = (end_date - start_date).days
    random_days = rng.integers(0, total_days, size=n_events)
    dates = start_date + pd.to_timedelta(random_days, unit="D")

    magnitudes = []
    for d_type in disaster_choices:
        if d_type == "earthquake":
            magnitudes.append(np.round(rng.normal(loc=5.5, scale=0.9), 2))
        else:
            magnitudes.append(np.round(rng.normal(loc=3.0, scale=0.8), 2))
    magnitudes = np.clip(np.array(magnitudes), 1.0, 9.5)

    base_people = rng.integers(50, 5000, size=n_events)
    affected_people = (base_people * (magnitudes ** 1.5)).astype(int)
    base_damage = rng.uniform(1e5, 5e7, size=n_events)
    economic_damage = base_damage * (magnitudes ** 1.7)

    df = pd.DataFrame(
        {
            "location": location_names,
            "disaster_type": disaster_choices,
            "magnitude": magnitudes,
            "date": dates,
            "affected_people": affected_people,
            "economic_damage": economic_damage,
            "latitude": latitudes,
            "longitude": longitudes,
        }
    )
    df.to_csv(csv_path, index=False)

df.head()
"""
        ),
        md("## 2. Keşifsel özet\n"),
        code(
            """print("Kayıt sayisi:", len(df))
print("Sutunlar:", df.columns.tolist())
df.describe(include="all")
"""
        ),
        md("## 3. Yıllara göre afet sıklığı\n"),
        code(
            """df["year"] = df["date"].dt.year
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
plt.xlabel("Yil")
plt.ylabel("Olay sayisi")
plt.legend(title="Afet tipi")
plt.tight_layout()
plt.show()
"""
        ),
        md("## 4. En cok etkilenen bolgeler\n"),
        code(
            """impact_by_region = (
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
plt.title(f"Etkilenen kisi sayisina gore ilk {top_n} bolge")
plt.xlabel("Toplam etkilenen kisi")
plt.ylabel("Konum")
plt.tight_layout()
plt.show()
top_regions
"""
        ),
        md("## 5. Buyukluk ve ekonomik zarar\n"),
        code(
            """sample = df.sample(min(400, len(df)), random_state=0)
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=sample,
    x="magnitude",
    y="economic_damage",
    hue="disaster_type",
    alpha=0.7,
)
plt.yscale("log")
plt.title("Buyukluk vs ekonomik zarar (log olcek)")
plt.xlabel("Buyukluk / siddet")
plt.ylabel("Ekonomik zarar (USD, log)")
plt.legend(title="Afet tipi")
plt.tight_layout()
plt.show()

corr_value = (
    df[["magnitude", "economic_damage"]]
    .assign(log_damage=np.log1p(df["economic_damage"]))
    .corr()
    .loc["magnitude", "log_damage"]
)
print(f"Buyukluk ile log(zarar) korelasyonu: {corr_value:.2f}")
"""
        ),
        md("## 6. Bolge risk skoru\n"),
        code(
            """region_risk = compute_region_risk_scores(df)
region_risk.head(10)
"""
        ),
        md(
            """## 7. Harita: yuksek riskli bolgeler

Folium ile etkilesimli harita; daire rengi ve boyutu risk skoruna gore.
"""
        ),
        code(
            """top_k = 10
top_risk_regions = region_risk.head(top_k).copy()
center_lat = top_risk_regions["latitude"].mean()
center_lon = top_risk_regions["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
risk_min = top_risk_regions["risk_score"].min()
risk_max = top_risk_regions["risk_score"].max()
eps = 1e-9
top_risk_regions["risk_norm"] = (top_risk_regions["risk_score"] - risk_min) / (
    risk_max - risk_min + eps
)

for _, row in top_risk_regions.iterrows():
    risk_norm = row["risk_norm"]
    radius = 50000 + 150000 * risk_norm
    color = "#ffcc00" if risk_norm < 0.5 else "#ff3300"
    popup_text = (
        f"<b>{row['location']}</b><br>"
        f"Risk: {row['risk_score']:.2f}<br>"
        f"Olay: {int(row['event_count'])}<br>"
        f"Ort. buyukluk: {row['avg_magnitude']:.2f}"
    )
    folium.Circle(
        location=[row["latitude"], row["longitude"]],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=folium.Popup(popup_text, max_width=300),
    ).add_to(m)

m
"""
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    out = Path(__file__).resolve().parent / "disaster_analysis.ipynb"
    out.write_text(json.dumps(NOTEBOOK, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK")  # avoid Windows console Unicode errors on long paths


if __name__ == "__main__":
    main()
