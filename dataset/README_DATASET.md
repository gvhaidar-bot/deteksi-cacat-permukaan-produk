# Dataset

## Sumber utama: NEU Surface Defect Database (NEU-DET)

- Pembuat: Kechen Song & Yunhui Yan, Northeastern University
- Isi: 1.800 citra grayscale 200×200 piksel permukaan baja hot-rolled
- Kelas (300 citra per kelas):
  - `crazing` — retakan halus berjejaring
  - `inclusion` — bintik inklusi
  - `patches` — bercak gelap besar
  - `pitted_surface` — permukaan berpori
  - `rolled-in_scale` — kerak oksida tergiling
  - `scratches` — goresan
- Split bawaan versi Kaggle: `train/` 1.440 citra, `validation/` 360 citra
- Anotasi: XML Pascal VOC berisi kotak ground truth setiap cacat
- Tautan: https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database
- Sitasi: Song, K. & Yan, Y. (2013), Applied Surface Science 285, 858–864

Semua citra pada dataset ini adalah citra **bercacat** — tidak ada kelas produk normal / bagus.

## Isi folder ini

- `contoh/` — 18 citra asli NEU (3 per kelas, diambil dari split validation nomor 241–243) + 2 citra `normal_sintetis`, dipakai aplikasi web sebagai contoh sekali klik. Folder ini ikut di-commit ke Git.
- `NEU-DET/` — dataset penuh hasil `python scripts/unduh_dataset.py` (±27 MB). Folder ini **tidak** ikut di-commit (ada di .gitignore); unduh sendiri bila ingin menjalankan evaluasi penuh.

## Citra normal sintetis

Folder `contoh/normal_sintetis/` berisi citra permukaan bersih yang **dibangkitkan secara program** (bidang abu + noise Gaussian + pola garis giling halus, lihat `scripts/buat_contoh_normal.py`). Tujuannya hanya untuk mendemonstrasikan keputusan LULUS dan memeriksa false positive, karena dataset NEU tidak menyediakan citra normal. Jangan menyebut citra ini sebagai foto produk asli pada laporan / video — sebut apa adanya: citra sintetis.
