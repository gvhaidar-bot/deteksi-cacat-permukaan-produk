# Outline Laporan (2–3 halaman) & Video Presentasi (≥10 menit)

Mengikuti Panduan Tugas Mandiri PCD (22TIF0262), jalur individu: video ≥10 menit + source code + laporan 2–3 halaman PDF, dikumpulkan via LMS paling lambat H-3 sebelum UAS.

## A. Struktur laporan

1. **Pendahuluan** — masalah quality control manual di industri manufaktur (lambat, subjektif, melelahkan), tujuan sistem deteksi cacat permukaan otomatis berbasis pengolahan citra.
2. **Dataset** — NEU Surface Defect Database: 1.800 citra grayscale 200×200, 6 kelas cacat × 300, split train/validation, anotasi XML. Catatan jujur: semua citra bercacat; citra normal untuk uji LULUS dibuat sintetis.
3. **Metodologi** — diagram pipeline 10 tahap (grayscale → blur → black-hat → top-hat → peta anomali → threshold Otsu → Canny → morfologi → kontur & fitur → keputusan). Jelaskan fungsi tiap tahap 1–2 kalimat dan alasan pemilihannya (mis. black-hat karena mayoritas cacat baja lebih gelap dari permukaan).
4. **Hasil & Analisis** — tabel evaluasi 360 citra validation: deteksi 360/360 (100%), lokalisasi kotak ground truth 706/854 (82,7%, IoU ≥ 0,10); per kelas tertinggi rolled-in scale 96,2% dan crazing 95,7%, terendah patches 63,0%. Sertakan 2–3 tangkapan layar tahapan (paling menarik: scratches dan crazing). Bahas keterbatasan: over-segmentasi pada crazing, patches bertepi kabur, dugaan jenis masih heuristik, false positive pada produk normal asli belum terukur.
5. **Kesimpulan** — pipeline klasik cukup untuk mendeteksi keberadaan cacat dan melokalisasi sebagian besar cacat tanpa pelatihan model; pengembangan lanjut: dataset produk normal asli + klasifikasi terlatih (mis. SVM/CNN) untuk jenis cacat.
6. **Daftar Pustaka** — Song & Yan (2013), dokumentasi OpenCV, halaman Kaggle dataset.

## B. Struktur video (target ±12 menit)

| Bagian | Durasi | Isi |
|---|---|---|
| Pembukaan | 1–2 mnt | Salam, perkenalan diri (nama, NIM, kelas), judul: Deteksi Cacat Permukaan Produk — Tema D |
| Motivasi | 1–2 mnt | QC manual vs otomatis; contoh kerugian produk cacat lolos ke pelanggan |
| Landasan teori | 2–3 mnt | Grayscale, filter Gaussian, morfologi (opening/closing, black-hat, top-hat), threshold Otsu, deteksi tepi Canny, kontur & fitur geometris |
| Metodologi | 2–3 mnt | Tampilkan diagram/skema pipeline 10 tahap + perkenalkan dataset NEU (6 kelas, tunjukkan contoh tiap kelas) |
| Demo program | 3–4 mnt | Jalankan `python backend/app.py`, buka web: (1) contoh scratches, (2) contoh patches, (3) citra normal sintetis → LULUS, (4) geser sensitivitas & luas minimum, jelaskan perubahan hasil |
| Hasil & analisis | 2–3 mnt | Tampilkan tabel hasil_evaluasi (100% deteksi, 82,7% lokalisasi), jelaskan patches terendah & over-segmentasi crazing sebagai keterbatasan |
| Kesimpulan | 1 mnt | Ringkasan + ide pengembangan |

Tips rekaman dari panduan: resolusi ≥720p, suara jernih, tampilkan wajah + layar (picture-in-picture, mis. OBS Studio), unggah YouTube Unlisted atau Google Drive (anyone with link can view).

## C. Checklist pengumpulan LMS

- [ ] Link video YouTube / Drive
- [ ] Source code (repo GitHub ini)
- [ ] Laporan 2–3 halaman (PDF)
