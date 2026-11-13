# Contoh Buah Segar & Busuk (Bahan Uji Mode Buah)

Sumber: Kaggle **Fruits and Vegetables Dataset** — Mukhiddinov et al. (2022), *Sensors* 22(21):8192.
https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset
Dataset penuh berisi 12.000 citra buah & sayur segar dan busuk (apel, pisang, jeruk, mangga, stroberi, dan sayuran), sebagian besar berlatar putih dengan satu buah per citra.

Isi folder ini (13 citra pilihan, semuanya terklasifikasi benar oleh Mode Buah):

- Buah busuk: apel (2), pisang (2), jeruk (2), mangga (2), stroberi (2)
- Buah segar pembanding: apel (1), pisang (1), jeruk (1)

## Cara memakai

Di web, pilih contoh buah apa pun di galeri — **Mode Buah** aktif otomatis. Untuk foto buah unggahan sendiri, pilih "Mode pemeriksaan: Buah & makanan" sebelum memproses.

## Tentang Mode Buah (ringkas)

Mode Buah (`backend/deteksi_buah.py`) berbeda dari Mode Baja: buah disegmentasi dari latar (jarak warna LAB dari warna sudut citra), daun hijau dikeluarkan dari analisis, lalu bercak busuk dicari hanya pada kulit buah — inti gelap terkonfirmasi (black-hat + piksel jauh lebih gelap dari median kulit) beserta wilayah penggelapan di sekitarnya dan jamur di dekat inti. Keputusan BUSUK bila luas bercak ≥ 2,5% luas kulit (preset Sedang).

Hasil uji pada 60 citra dataset ini (6 per kelas, 13 Nov 2026): **41/60 tepat (68,3%)**. Terbaik: mangga busuk 6/6, jeruk segar 6/6, stroberi segar 6/6. Terlemah: apel segar 1/6 (belang merah alami apel terbaca sebagai penggelapan) dan stroberi busuk 2/6 (jamur putih/abu tidak selalu punya inti gelap). Mode Baja pada foto buah tidak valid — contohnya jeruk segar berdaun divonis CACAT 33,8% oleh Mode Baja, tetapi SEGAR 1,8% oleh Mode Buah, karena daun dan tetesan air tidak lagi dihitung sebagai cacat.
