# Contoh Buah Segar & Busuk (Bahan Uji Tambahan)

Sumber: Kaggle **Fruits and Vegetables Dataset** — Mukhiddinov et al. (2022), *Sensors* 22(21):8192.
https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset
Dataset penuh berisi 12.000 citra buah & sayur segar dan busuk (apel, pisang, jeruk, mangga, stroberi, dan sayuran), sebagian besar berlatar putih dengan satu buah per citra.

Isi folder ini (13 citra pilihan):

- Buah busuk: apel (2), pisang (2), jeruk (2), mangga (2), stroberi (2) — dipilih yang area busuknya paling jelas terlihat
- Buah segar pembanding: apel (1), pisang (1), jeruk (1)

## Hasil uji jujur pada aplikasi ini (13 Nov 2026)

Pipeline aplikasi ini dirancang untuk permukaan **baja** (citra keabuan bertekstur seragam). Saat diuji pada 60 citra buah (30 segar + 30 busuk, 6 per kelas):

- 30/30 buah **busuk** terdeteksi CACAT — area gelap busuknya memang ter-highlight pada visualisasi hasil.
- 30/30 buah **segar juga ikut terdeteksi CACAT** — tekstur kulit, bayangan, tangkai, dan biji stroberi terbaca sebagai cacat oleh pipeline baja.

Artinya folder ini cocok untuk **mendemonstrasikan bahwa area busuk terlihat oleh detektor**, tetapi aplikasi versi baja **belum bisa membedakan buah segar vs busuk**. Pembedaan itu butuh mode khusus buah: segmentasi buah dari latar + analisis warna HSV (bercak coklat/hitam busuk dan jamur), yang merupakan topik spesifik lain pada Tema D panduan tugas ("Quality control buah/sayuran di conveyor belt").
