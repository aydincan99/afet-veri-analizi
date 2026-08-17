# Afet Veri Analizi Platformu

Türkiye'nin 81 ili için sentetik deprem ve sel olaylarını analiz eden, bölgesel risk profillerini görselleştiren veri bilimi platformu. Streamlit arayüzü, komut satırı analiz scripti ve Jupyter notebook ile etkileşimli keşif imkânı sunar.

**Teknolojiler:** Python · Streamlit · Pandas · Matplotlib · Seaborn · Folium · Jupyter

---

## Geliştirici

**Aydın Candemiır**

---

## Özellikler

- 81 il için bölgesel deprem/sel profili ve nüfus ağırlıklı sentetik olay üretimi
- Yıllara göre olay sıklığı, en çok etkilenen iller, büyüklük–zarar ilişkisi analizi
- İl bazlı risk skoru hesaplama (frekans, büyüklük, etkilenen kişi, ekonomik zarar)
- Folium tabanlı interaktif harita görselleştirmesi
- Statik grafik export (`run_analysis.py`) ve notebook tabanlı analiz

> **Not:** Olay verileri sentetiktir; gerçek AFAD/TÜİK kayıtları değildir. Meta veri (`data/iller_81.csv`) 81 il plaka sırası, merkez koordinatları ve yaklaşık nüfus bilgisini içerir.

---

## Gereksinimler

- Python 3.10 veya üzeri
- İlk kurulumda internet bağlantısı

---

## Kurulum

```bash
git clone https://github.com/aydincan99/afet-veri-analizi.git
cd afet-veri-analizi
python -m venv .venv
```

**Windows:** `.venv\Scripts\activate`  
**macOS / Linux:** `source .venv/bin/activate`

```bash
python -m pip install -U pip
python -m pip install -r requirements.txt
```

---

## Çalıştırma

### Web arayüzü (önerilen)

```bash
python -m streamlit run app.py
```

Tarayıcı: **http://localhost:8501**

### Grafikleri dosyaya export

```bash
python run_analysis.py
```

Çıktı: `outputs/` klasörü (gitignore'da; yerelde oluşur)

### Jupyter notebook

```bash
python -m notebook
```

`notebooks/disaster_analysis.ipynb`

---

## Proje yapısı

| Dosya / klasör | Açıklama |
|---|---|
| `app.py` | Streamlit dashboard |
| `run_analysis.py` | PNG/HTML grafik export |
| `data/iller_81.csv` | 81 il meta verisi |
| `src/data_loader.py` | Veri yükleme ve sentetik üretim |
| `src/risk_utils.py` | İl risk skoru hesaplama |
| `notebooks/` | Keşifsel analiz notebook'ları |

---

## Lisans

Eğitim ve portfolyo amaçlıdır.
