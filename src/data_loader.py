"""
Turkiye 81 ili odakli ornek afet verisi.

- Il meta: data/iller_81.csv (plaka sirasi, merkez koordinat, TUIK'e yakin nufus 2022,
  bolge: Marmara/Ege/Akdeniz/Ic Anadolu/Karadeniz/Dogu/Guneydogu — deprem ve sel
  agirliklari bu bolge kodundan turetilir).
- Afet satirlari sentetiktir; gercek olay dogrulugu icin AFAD / TUIK / EM-DAT vb.
  resmi verilerle birlestirilmelidir.

Uretilen CSV: data/turkiye_afet_81il.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATA_CSV = "turkiye_afet_81il.csv"
ILLER_CSV = "iller_81.csv"

# bolge: 1=Marmara, 2=Ege, 3=Akdeniz, 4=Ic Anadolu, 5=Karadeniz, 6=Dogu Anadolu, 7=Guneydogu
# (deprem, sel) goreceli skorlar — PGA/sel haritalarinin kabaca ozeti, bilimsel model degildir
BOLGE_TABLO: dict[int, tuple[float, float]] = {
    1: (0.88, 0.19),
    2: (0.76, 0.15),
    3: (0.58, 0.30),
    4: (0.38, 0.12),
    5: (0.50, 0.76),
    6: (0.90, 0.21),
    7: (0.86, 0.29),
}


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_data_path() -> Path:
    return project_root() / "data" / DEFAULT_DATA_CSV


def load_iller_81() -> pd.DataFrame:
    path = project_root() / "data" / ILLER_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Eksik: {path}. 81 il meta dosyasi projede bulunmali."
        )
    iller = pd.read_csv(path, encoding="utf-8")
    if len(iller) != 81:
        raise ValueError(f"iller_81.csv 81 satir olmali, bulunan: {len(iller)}")
    unknown = set(iller["bolge"].unique()) - set(BOLGE_TABLO.keys())
    if unknown:
        raise ValueError(f"Bilinmeyen bolge kodu: {unknown}")
    iller = iller.sort_values("plaka").reset_index(drop=True)
    base_dep = iller["bolge"].map(lambda b: BOLGE_TABLO[int(b)][0]).to_numpy(dtype=float)
    base_sel = iller["bolge"].map(lambda b: BOLGE_TABLO[int(b)][1]).to_numpy(dtype=float)
    plaka = iller["plaka"].to_numpy(dtype=float)
    # Il bazinda kucuk deterministik fark (tekrarlanabilir)
    dep_f = base_dep + 0.034 * np.sin(plaka * 0.73)
    sel_f = base_sel + 0.038 * np.cos(plaka * 0.61)
    iller["deprem"] = np.clip(dep_f, 0.16, 0.96)
    iller["sel"] = np.clip(sel_f, 0.10, 0.90)
    return iller


def load_or_create_data(csv_path: Path | None = None) -> pd.DataFrame:
    if csv_path is None:
        csv_path = default_data_path()
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_path.exists():
        return pd.read_csv(csv_path, parse_dates=["date"], encoding="utf-8")

    iller = load_iller_81()
    rng = np.random.default_rng(seed=42)
    n_il = len(iller)
    isimler = iller["il_adi"].tolist()
    latlar = iller["lat"].to_numpy(dtype=float)
    lonlar = iller["lon"].to_numpy(dtype=float)
    nufus = iller["nufus"].to_numpy(dtype=float)
    dep = iller["deprem"].to_numpy(dtype=float)
    sel = iller["sel"].to_numpy(dtype=float)

    # Bolge secimi: (dep+sel) * sqrt(nufus) — buyuk ve riskli illerde daha fazla olay
    bolge_agirlik = (dep + sel + 0.06) * np.sqrt(np.clip(nufus, 1.0, None))
    bolge_agirlik /= bolge_agirlik.sum()

    # 81 il ile orantili orneklem (yaklasik 14-15 olay/il / 25 yil)
    n_events = int(15 * n_il)
    start = pd.Timestamp("2000-01-01")
    end = pd.Timestamp("2025-12-31")
    gun = (end - start).days

    bolge_ix = rng.choice(n_il, size=n_events, p=bolge_agirlik)
    tarihler = start + pd.to_timedelta(rng.integers(0, gun, size=n_events), unit="D")

    afet_tipleri: list[str] = []
    buyuklukler: list[float] = []
    pop_scale = np.log10(np.clip(nufus, 10_000.0, None))

    for i in range(n_events):
        ix = bolge_ix[i]
        d, s = dep[ix], sel[ix]
        toplam = d + s + 1e-6
        sel_olasilik = s / toplam

        if rng.random() < sel_olasilik:
            tip = "sel"
            s_raw = np.clip(rng.normal(3.45, 0.52), 2.0, 6.2)
            if s >= 0.58:
                s_raw = np.clip(s_raw + rng.uniform(0.0, 0.55), 2.0, 6.6)
            buyuklukler.append(round(float(s_raw), 2))
        else:
            tip = "deprem"
            temel = rng.normal(4.85, 0.52)
            if rng.random() < 0.055:
                temel += rng.uniform(0.85, 1.75)
            if d >= 0.82:
                temel += rng.uniform(0.08, 0.42)
            temel += 0.12 * (pop_scale[ix] - 6.0) * 0.15
            ml = float(np.clip(temel, 3.5, 7.6))
            buyuklukler.append(round(ml, 2))
        afet_tipleri.append(tip)

    mags = np.array(buyuklukler)
    loc_names = [f"{isimler[bolge_ix[i]]}, Turkiye" for i in range(n_events)]
    lats = latlar[bolge_ix] + rng.normal(0, 0.035, size=n_events)
    lons = lonlar[bolge_ix] + rng.normal(0, 0.035, size=n_events)

    etkilenen: list[int] = []
    zarar: list[float] = []
    for i in range(n_events):
        ix = bolge_ix[i]
        ps = float(pop_scale[ix])
        mag = float(mags[i])
        tip = afet_tipleri[i]

        if tip == "deprem":
            log_mu = 4.8 + 1.12 * ps + 0.58 * max(0.0, mag - 4.15)
            etk = int(np.clip(rng.lognormal(log_mu, 0.40), 80, 2_500_000))
            baz = rng.lognormal(15.15, 0.62) * (10 ** ((ps - 5.8) * 0.22))
            zar = baz * (10 ** (np.clip(mag, 3.5, 7.5) - 4.55))
        else:
            log_mu = 4.35 + 1.02 * ps + 0.38 * max(0.0, mag - 2.4)
            etk = int(np.clip(rng.lognormal(log_mu, 0.36), 50, 1_300_000))
            baz = rng.lognormal(14.55, 0.58) * (10 ** ((ps - 5.8) * 0.2))
            zar = baz * (mag / 3.15) ** 1.75

        etkilenen.append(etk)
        zarar.append(float(np.clip(zar, 5e4, 4.5e10)))

    df = pd.DataFrame(
        {
            "location": loc_names,
            "disaster_type": afet_tipleri,
            "magnitude": mags,
            "date": tarihler,
            "affected_people": etkilenen,
            "economic_damage": zarar,
            "latitude": lats,
            "longitude": lons,
        }
    )
    df.to_csv(csv_path, index=False, encoding="utf-8")
    return df
