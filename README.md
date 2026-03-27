# Afet verisi analizi (Türkiye, 81 il)

Sentetik deprem ve sel olaylarıyla bölgesel risk özeti; **Streamlit** ar yüzü, **Jupyter** not defteri ve komut satırı scripti içerir. Meta veri: 81 il plaka sırası, merkez koordinatlar ve yaklaşık nüfus (`data/iller_81.csv`). Olay tabloları çalıştırınca üretilir (gerçek AFAD/TÜİK kaydı değildir).

## Özellikler

- Türkiye 81 ili; bölgesel deprem/sel profili + nüfusla ağırlıklı sentetik olaylar
- Yıllara göre sıklık, en çok etkilenen iller, büyüklük–zarar ilişkisi
- Basit il risk skoru ve harita (Türkiye)

## Gereksinimler

- Python 3.10+

## Kurulum

```bash
git clone <repo-url>
cd afet-veri-analizi
python -m venv .venv
```

**Windows:** `.venv\Scripts\activate`  
**macOS/Linux:** `source .venv/bin/activate`

```bash
python -m pip install -r requirements.txt
```

## Çalıştırma

### Web arayüzü (önerilen)

```bash
python -m streamlit run app.py
```

Tarayıcı: [http://localhost:8501](http://localhost:8501)

### Grafikleri dosyaya yazmak

```bash
python run_analysis.py
```

Çıktı: `outputs/` (`.gitignore` ile repoda tutulmaz; yerelde oluşur.)

### Jupyter

```bash
python -m notebook
```

`notebooks/disaster_analysis.ipynb` (not: not defteri eski dünya örneği içerebilir; güncel mantık `src/data_loader.py` ile aynı hizaya getirilebilir.)

## Proje yapısı

| Yol | Açıklama |
|-----|----------|
| `app.py` | Streamlit uygulaması |
| `run_analysis.py` | PNG/HTML export |
| `data/iller_81.csv` | 81 il meta (commitlenir) |
| `data/turkiye_afet_81il.csv` | Üretilen olaylar (ignore; ilk çalıştırmada oluşur) |
| `src/data_loader.py` | Veri yükleme / sentetik üretim |
| `src/risk_utils.py` | İl risk skoru |

## English summary

Synthetic earthquake and flood events for Turkish provinces (metadata for all 81 provinces). Run Streamlit for interactive dashboards; use `run_analysis.py` for static charts. Generated CSVs and `outputs/` are gitignored—recreate locally after clone.

## Lisans

İhtiyacınıza göre bir lisans ekleyin (ör. MIT).
