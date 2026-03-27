"""
Sade Streamlit arayuzu. Calistirma (proje kokunden):
  streamlit run app.py
"""
from __future__ import annotations

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium

from src.data_loader import load_or_create_data
from src.risk_utils import compute_region_risk_scores

st.set_page_config(page_title="Afet analizi", layout="wide")

st.title("Turkiye afet risk analizi")
st.caption(
    "81 il (plaka, merkez koordinat, nufus ~2022) + bolgesel deprem/sel profili; "
    "olaylar sentetik — gercek dogruluk icin resmi veri (AFAD, TUIK vb.) eklenmelidir."
)


@st.cache_data
def get_df() -> pd.DataFrame:
    return load_or_create_data()


df = get_df()
df_work = df.copy()
df_work["year"] = df_work["date"].dt.year

region_risk = compute_region_risk_scores(df)
corr = (
    df[["magnitude", "economic_damage"]]
    .assign(log_damage=np.log1p(df["economic_damage"]))
    .corr()
    .loc["magnitude", "log_damage"]
)

c1, c2, c3 = st.columns(3)
c1.metric("Kayit", f"{len(df):,}")
c2.metric("Bolge sayisi", f"{df['location'].nunique()}")
c3.metric("Buyukluk / log(zarar) r", f"{corr:.2f}")

sns.set_theme(style="whitegrid", font_scale=1.0)

# --- Siklik
events = (
    df_work.groupby(["year", "disaster_type"])["location"]
    .count()
    .reset_index(name="n")
)
fig1, ax1 = plt.subplots(figsize=(10, 3.5))
sns.lineplot(data=events, x="year", y="n", hue="disaster_type", marker="o", ax=ax1)
ax1.set_title("Yillara gore olay sayisi")
ax1.set_xlabel("Yil")
ax1.set_ylabel("Olay")
ax1.legend(title="Afet")
fig1.tight_layout()
st.pyplot(fig1, clear_figure=True)
plt.close(fig1)

# --- Bolgeler + sacilim
left, right = st.columns(2)
with left:
    impact = (
        df.groupby("location")["affected_people"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=impact,
        x="affected_people",
        y="location",
        hue="location",
        palette="Reds_r",
        legend=False,
        ax=ax2,
    )
    ax2.set_title("En cok etkilenen bolgeler")
    ax2.set_xlabel("Etkilenen kisi")
    ax2.set_ylabel("")
    fig2.tight_layout()
    st.pyplot(fig2, clear_figure=True)
    plt.close(fig2)

with right:
    sample = df.sample(min(350, len(df)), random_state=0)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=sample,
        x="magnitude",
        y="economic_damage",
        hue="disaster_type",
        alpha=0.65,
        ax=ax3,
    )
    ax3.set_yscale("log")
    ax3.set_title("Buyukluk ve ekonomik zarar")
    ax3.set_xlabel("Deprem (ML) / sel siddet indeksi")
    ax3.set_ylabel("Zarar (USD, log)")
    fig3.tight_layout()
    st.pyplot(fig3, clear_figure=True)
    plt.close(fig3)

st.subheader("Bolge risk siralamasi")
st.dataframe(
    region_risk[
        [
            "location",
            "risk_score",
            "event_count",
            "avg_magnitude",
            "avg_affected_people",
            "avg_economic_damage",
        ]
    ].head(15),
    use_container_width=True,
    hide_index=True,
)

# --- Harita: sadece Turkiye
st.subheader("Yuksek riskli iller (Turkiye)")
top = region_risk.head(12).copy()
m = folium.Map(location=[39.0, 35.2], zoom_start=6, tiles="cartodbpositron")
rmin, rmax = top["risk_score"].min(), top["risk_score"].max()
eps = 1e-9
top["rn"] = (top["risk_score"] - rmin) / (rmax - rmin + eps)
for _, row in top.iterrows():
    rn = row["rn"]
    folium.Circle(
        location=[row["latitude"], row["longitude"]],
        radius=12000 + 38000 * rn,
        color="#c0392b" if rn >= 0.5 else "#b7950b",
        fill=True,
        fill_opacity=0.35,
        popup=folium.Popup(
            f"{row['location']}<br>Skor: {row['risk_score']:.2f}",
            max_width=220,
        ),
    ).add_to(m)

st_folium(m, width=None, height=420, key="risk_map", returned_objects=[])
