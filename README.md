# Deteksi Cacat / Kerusakan Permukaan Produk

Tugas Mandiri Pengolahan Citra Digital (22TIF0262) — **Tema D: Industri dan Manufaktur**
Topik spesifik: *Deteksi cacat/kerusakan permukaan produk* (quality control permukaan baja)

Aplikasi web untuk memeriksa foto permukaan produk (baja) dan memutuskan **LULUS** atau **CACAT**, lengkap dengan lokasi cacat, luas area cacat, tingkat keparahan, dan dugaan jenis cacat. Seluruh deteksi memakai **pengolahan citra digital klasik** (bukan model machine learning terlatih), sehingga setiap tahapnya bisa dijelaskan langkah demi langkah.

- **Frontend:** HTML, CSS, JavaScript murni (folder `frontend/`)
- **Backend:** Python + Flask + OpenCV (folder `backend/`)

## Dataset

**NEU Surface Defect Database** (NEU-DET) — Song & Yan, Northeastern University, dibagikan lewat Kaggle (sumber dataset yang dianjurkan pada panduan tugas):

- 1.800 citra **grayscale 200×200 piksel** permukaan baja hot-rolled
- 6 jenis cacat, masing-masing 300 citra:
  - `crazing` — retakan halus berjejaring
  - `inclusion` — bintik inklusi
  - `patches` — bercak gelap besar
  - `pitted_surface` — permukaan berpori / berlubang kecil
  - `rolled-in_scale` — kerak oksida tergiling
  - `scratches` — goresan
- Pembagian bawaan Kaggle: `train` 1.440 citra + `validation` 360 citra, lengkap dengan anotasi kotak ground truth (XML Pascal VOC)
- Unduh: https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database

Di dalam repo ini sudah disertakan **20 citra contoh** di `dataset/contoh/` (3 citra asli NEU per kelas + 2 citra `normal_sintetis`) agar aplikasi langsung bisa didemo tanpa mengunduh dataset penuh. Dataset NEU hanya berisi citra **bercacat** — tidak ada citra produk normal — jadi citra permukaan bersih dibuat secara sintetis (tekstur + noise Gaussian) khusus untuk menguji keputusan LULUS, dan diberi label jelas sebagai sintetis.

Untuk mengunduh dataset penuh (±27 MB) ke folder `dataset/NEU-DET/`:

```
python scripts/unduh_dataset.py
```

## Pipeline Pengolahan Citra

Semua tahap ada di `backend/deteksi.py` dan divisualkan satu per satu di halaman web:

1. **Grayscale** — konversi citra ke 1 kanal keabuan.
2. **Gaussian Blur 5×5** — menekan noise butiran permukaan baja.
3. **Black-Hat** (closing − citra, kernel elips 31×31) — menonjolkan cacat yang *lebih gelap* dari sekitarnya (goresan, bercak, lubang).
4. **Top-Hat** (citra − opening) — menonjolkan cacat yang *lebih terang* dari sekitarnya.
5. **Peta Anomali** — black-hat + top-hat.
6. **Segmentasi Threshold Otsu** — ambang otomatis × faktor sensitivitas (Rendah 1,35 · Sedang 1,15 · Tinggi 0,95).
7. **Deteksi Tepi Canny** — menangkap struktur tipis (goresan/retakan); tepi hanya diterima bila didukung peta anomali.
8. **Morfologi Opening & Closing** — membuang bintik noise dan menyambung area cacat yang terputus.
9. **Analisis Kontur** — setiap kontur diukur: luas, keliling, kotak pembatas, rasio aspek, sirkularitas. Kontur di bawah luas minimum (preset: 260 / 120 / 60 piksel) diabaikan.
10. **Keputusan** — dugaan jenis dari fitur geometris (rasio aspek ≥ 4 → goresan; kontur kecil & bulat → titik inklusi/pori; dsb.). Verdict **CACAT** bila total luas cacat ≥ 0,8% luas citra, selain itu **LULUS**. Keparahan: Ringan < 3%, Sedang 3–10%, Berat > 10%.

## Hasil Evaluasi (Data Asli, Bukan Perkiraan)

Skrip `scripts/evaluasi.py` menjalankan pipeline pada **seluruh 360 citra validation NEU-DET** (sensitivitas Sedang) dan membandingkan kotak hasil deteksi dengan kotak ground truth XML (terlokalisasi bila IoU ≥ 0,10). Hasil lengkap tersimpan di `hasil_evaluasi/hasil_evaluasi.json` dan `.csv`.

| Kelas | Citra terdeteksi cacat | Kotak GT terlokalisasi | Rata-rata luas cacat |
|---|---|---|---|
| crazing | 60/60 (100%) | 155/162 (95,7%) | 71,97% |
| inclusion | 60/60 (100%) | 115/147 (78,2%) | 12,04% |
| patches | 60/60 (100%) | 116/184 (63,0%) | 38,19% |
| pitted_surface | 60/60 (100%) | 91/105 (86,7%) | 33,08% |
| rolled-in_scale | 60/60 (100%) | 127/132 (96,2%) | 23,04% |
| scratches | 60/60 (100%) | 102/124 (82,3%) | 9,21% |
| **Total** | **360/360 (100%)** | **706/854 (82,7%)** | — |

Uji citra normal sintetis (10 citra permukaan bersih): **0% area ter-flag, semua diputuskan LULUS**.

### Catatan analisis & keterbatasan (jujur)

- Tingkat deteksi 100% di atas adalah *recall pada citra bercacat* — dataset NEU tidak punya citra normal asli, jadi angka false-positive pada produk normal sungguhan belum terukur; uji normal baru dilakukan pada citra sintetis.
- Kelas `patches` paling sulit dilokalisasi (63,0%): bercak besar bertepi kabur membuat kotak hasil segmentasi sering lebih kecil / terpecah dibanding kotak ground truth.
- Luas masker `crazing` besar (rata-rata 71,97%) karena retakannya memang menyebar hampir ke seluruh permukaan, tetapi sebagian tekstur latar ikut tersegmentasi (over-segmentasi) — terlihat pada visualisasi tahap masker.
- Dugaan jenis bersifat heuristik geometris, bukan klasifikasi terlatih; dua kelas yang mirip bentuknya (mis. patches vs rolled-in scale) bisa tertukar.

## Cara Menjalankan

Butuh Python 3.10+ (disarankan 3.12/3.13; bila `pip install` OpenCV gagal di Python 3.15, pakai Python 3.13 berdampingan).

```
python -m venv .venv
.venv\Scripts\activate        (Windows)   |   source .venv/bin/activate   (Linux/macOS)
pip install -r backend/requirements.txt
python backend/app.py
```

Buka **http://127.0.0.1:5000** di browser. Unggah citra produk atau klik citra contoh dataset, atur sensitivitas, lalu klik **Proses Deteksi**.

Menjalankan evaluasi pada dataset penuh (setelah `scripts/unduh_dataset.py`):

```
python scripts/evaluasi.py --folder dataset/NEU-DET/validation
```

## Struktur Folder

```
backend/    app.py (server Flask + API) · deteksi.py (pipeline citra) · requirements.txt
frontend/   index.html · style.css · script.js
dataset/    contoh/ (20 citra contoh) · README_DATASET.md
scripts/    unduh_dataset.py · evaluasi.py · buat_contoh_normal.py
docs/       outline-laporan-dan-video.md
hasil_evaluasi/  hasil_evaluasi.json · hasil_evaluasi.csv
```

## Referensi

- Song, K. & Yan, Y. (2013). *A noise robust method based on completed local binary patterns for hot-rolled steel strip surface defects.* Applied Surface Science, 285, 858–864.
- Halaman dataset NEU: http://faculty.neu.edu.cn/songkc/en/zdylm/263273/list/index.htm (mirror Kaggle pada tautan dataset di atas)
- Dokumentasi OpenCV: https://docs.opencv.org/
