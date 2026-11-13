import os

import cv2


def _muat_cascade(nama_berkas):
    path = os.path.join(cv2.data.haarcascades, nama_berkas)
    cascade = cv2.CascadeClassifier(path)
    return None if cascade.empty() else cascade


_CASCADE_WAJAH = _muat_cascade("haarcascade_frontalface_default.xml")
_CASCADE_WAJAH_ALT = _muat_cascade("haarcascade_frontalface_alt2.xml")


def _kotak_saling_tumpang(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    if x2 <= x1 or y2 <= y1:
        return False
    luas_tumpang = (x2 - x1) * (y2 - y1)
    luas_terkecil = min(aw * ah, bw * bh)
    return luas_tumpang >= 0.35 * luas_terkecil


def _deteksi(cascade, abu, sisi_min):
    if cascade is None:
        return []
    hasil = cascade.detectMultiScale(
        abu,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(sisi_min, sisi_min),
    )
    return [tuple(int(v) for v in kotak) for kotak in hasil]


def hitung_wajah(gambar):
    if len(gambar.shape) == 2:
        abu = gambar.copy()
    else:
        abu = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)
    tinggi, lebar = abu.shape
    if max(tinggi, lebar) < 300:
        abu = cv2.resize(abu, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
        tinggi, lebar = abu.shape
    abu = cv2.equalizeHist(abu)
    sisi_min = max(28, int(min(tinggi, lebar) * 0.12))

    daftar_utama = _deteksi(_CASCADE_WAJAH, abu, sisi_min)
    if not daftar_utama:
        return 0
    daftar_alt = _deteksi(_CASCADE_WAJAH_ALT, abu, sisi_min)
    terkonfirmasi = 0
    for kotak in daftar_utama:
        if any(_kotak_saling_tumpang(kotak, lain) for lain in daftar_alt):
            terkonfirmasi += 1
    return terkonfirmasi
