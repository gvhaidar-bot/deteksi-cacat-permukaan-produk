import cv2
import numpy as np


PRESET_SENSITIVITAS = {
    "rendah": {"ambang_persen": 4.0, "faktor_luas_min": 2.0},
    "sedang": {"ambang_persen": 2.5, "faktor_luas_min": 1.0},
    "tinggi": {"ambang_persen": 1.5, "faktor_luas_min": 0.6},
}


def tingkat_keparahan(rasio_persen):
    if rasio_persen < 6.0:
        return "Ringan"
    if rasio_persen < 15.0:
        return "Sedang"
    return "Berat"


def _segmentasi_produk(gambar):
    tinggi, lebar = gambar.shape[:2]
    lab = cv2.cvtColor(gambar, cv2.COLOR_BGR2LAB).astype(np.float32)
    s = max(6, int(min(tinggi, lebar) * 0.06))
    sudut = np.concatenate(
        [
            lab[:s, :s].reshape(-1, 3),
            lab[:s, -s:].reshape(-1, 3),
            lab[-s:, :s].reshape(-1, 3),
            lab[-s:, -s:].reshape(-1, 3),
        ]
    )
    warna_latar = np.median(sudut, axis=0)
    jarak = np.linalg.norm(lab - warna_latar, axis=2)
    masker = (jarak > 26).astype(np.uint8) * 255
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    masker = cv2.morphologyEx(masker, cv2.MORPH_CLOSE, k5, iterations=2)
    masker = cv2.morphologyEx(masker, cv2.MORPH_OPEN, k5, iterations=1)
    kontur, _ = cv2.findContours(masker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if kontur:
        terbesar = max(kontur, key=cv2.contourArea)
        hasil = np.zeros((tinggi, lebar), dtype=np.uint8)
        cv2.drawContours(hasil, [terbesar], -1, 255, -1)
        cakupan = float((hasil > 0).sum()) / (tinggi * lebar)
        if 0.05 <= cakupan <= 0.97:
            return hasil, cakupan, True
    return np.full((tinggi, lebar), 255, dtype=np.uint8), 1.0, False


def _masker_daun(gambar, hsv, masker_produk):
    daun_hsv = cv2.inRange(hsv, np.array([28, 85, 30]), np.array([92, 255, 255]))
    b, g, r = cv2.split(gambar.astype(np.int16))
    daun_rgb = ((g > r + 10) & (g > b + 10) & (hsv[:, :, 1] > 70)).astype(np.uint8) * 255
    daun = cv2.bitwise_or(daun_hsv, daun_rgb)
    return cv2.bitwise_and(daun, daun, mask=masker_produk)


def proses_deteksi_buah(gambar, sensitivitas="sedang", luas_minimum=None):
    preset = PRESET_SENSITIVITAS.get(sensitivitas, PRESET_SENSITIVITAS["sedang"])
    if len(gambar.shape) == 2:
        asli = cv2.cvtColor(gambar, cv2.COLOR_GRAY2BGR)
    else:
        asli = gambar.copy()
    tinggi, lebar = asli.shape[:2]
    total_piksel = float(tinggi * lebar)

    masker_produk, cakupan, segmentasi_ok = _segmentasi_produk(asli)
    hsv = cv2.cvtColor(asli, cv2.COLOR_BGR2HSV)
    daun = _masker_daun(asli, hsv, masker_produk)
    kulit = cv2.subtract(masker_produk, daun)

    tepi_dalam = max(3, int(min(tinggi, lebar) * 0.02))
    kernel_tepi = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (tepi_dalam * 2 + 1, tepi_dalam * 2 + 1)
    )
    kulit_aman = cv2.erode(kulit, kernel_tepi, iterations=1)
    luas_kulit = float((kulit_aman > 0).sum())
    if luas_kulit < 0.02 * total_piksel:
        kulit_aman = kulit
        luas_kulit = float((kulit_aman > 0).sum())

    abu = cv2.cvtColor(asli, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(cv2.medianBlur(abu, 7), (9, 9), 0)
    ukuran_kernel = int(min(tinggi, lebar) * 0.09) | 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ukuran_kernel, ukuran_kernel))
    blackhat = cv2.morphologyEx(blur, cv2.MORPH_BLACKHAT, kernel)
    blackhat = cv2.bitwise_and(blackhat, blackhat, mask=kulit_aman)

    nilai_v = hsv[:, :, 2].astype(np.float32)
    nilai_s = hsv[:, :, 1]
    piksel_kulit = nilai_v[kulit_aman > 0]
    median_v = float(np.median(piksel_kulit)) if piksel_kulit.size else 0.0

    sangat_gelap = ((nilai_v < median_v * 0.55) & (kulit_aman > 0)).astype(np.uint8) * 255
    kuat = cv2.threshold(blackhat, 40, 255, cv2.THRESH_BINARY)[1]
    inti = np.zeros((tinggi, lebar), dtype=np.uint8)
    kontur_kuat, _ = cv2.findContours(kuat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    luas_min_inti = max(30.0, luas_kulit * 0.0008)
    for k in kontur_kuat:
        luas = cv2.contourArea(k)
        if luas < luas_min_inti:
            continue
        masker_k = np.zeros((tinggi, lebar), dtype=np.uint8)
        cv2.drawContours(masker_k, [k], -1, 255, -1)
        tumpang = float(((masker_k > 0) & (sangat_gelap > 0)).sum())
        rata = float(blackhat[masker_k > 0].mean()) if luas else 0.0
        if tumpang >= 0.12 * luas or rata >= 60:
            cv2.drawContours(inti, [k], -1, 255, -1)

    ringan_gelap = ((nilai_v < median_v * 0.76) & (kulit_aman > 0)).astype(np.uint8) * 255
    sedang_mask = cv2.threshold(blackhat, 24, 255, cv2.THRESH_BINARY)[1]
    jamur = (
        (nilai_s < 55) & (nilai_v > 70) & (nilai_v < 235) & (kulit_aman > 0)
    ).astype(np.uint8) * 255
    jamur = cv2.bitwise_and(
        jamur, cv2.dilate(inti, np.ones((15, 15), np.uint8), iterations=1)
    )
    wilayah = cv2.bitwise_or(cv2.bitwise_or(ringan_gelap, sedang_mask), jamur)
    wilayah = cv2.morphologyEx(wilayah, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=1)

    if luas_minimum is not None:
        luas_min = float(max(10, luas_minimum))
    else:
        luas_min = max(40.0, luas_kulit * 0.0012) * preset["faktor_luas_min"]

    jumlah_label, label, statistik, _ = cv2.connectedComponentsWithStats(wilayah, connectivity=8)
    masker_busuk = np.zeros((tinggi, lebar), dtype=np.uint8)
    for i in range(1, jumlah_label):
        if statistik[i, cv2.CC_STAT_AREA] < luas_min:
            continue
        komponen = (label == i).astype(np.uint8) * 255
        inti_di_komponen = int(((komponen > 0) & (inti > 0)).sum())
        if inti_di_komponen >= max(20, 0.003 * statistik[i, cv2.CC_STAT_AREA]):
            masker_busuk = cv2.bitwise_or(masker_busuk, komponen)

    luas_busuk = float((masker_busuk > 0).sum())
    rasio = luas_busuk / luas_kulit * 100 if luas_kulit else 0.0
    ambang_persen = preset["ambang_persen"]
    busuk = rasio >= ambang_persen

    kontur_busuk, _ = cv2.findContours(masker_busuk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    kontur_busuk = sorted(kontur_busuk, key=cv2.contourArea, reverse=True)
    hasil = asli.copy()
    daftar = []
    for indeks, k in enumerate(kontur_busuk, start=1):
        luas = float(cv2.contourArea(k))
        x, y, w, h = cv2.boundingRect(k)
        daftar.append(
            {
                "nomor": indeks,
                "jenis_dugaan": "Bercak busuk / jamur",
                "luas_piksel": int(round(luas)),
                "luas_persen": round(luas / luas_kulit * 100, 3) if luas_kulit else 0.0,
                "kotak": {"x": int(x), "y": int(y), "lebar": int(w), "tinggi": int(h)},
                "keliling": round(float(cv2.arcLength(k, True)), 1),
            }
        )
        cv2.drawContours(hasil, [k], -1, (0, 0, 255), 2)
        cv2.rectangle(hasil, (x, y), (x + w, y + h), (255, 120, 0), 2)
        cv2.putText(
            hasil,
            str(indeks),
            (x, max(14, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 120, 0),
            2,
            cv2.LINE_AA,
        )

    hist = cv2.calcHist([abu], [0], None, [256], [0, 256]).flatten()
    probabilitas = hist / max(1.0, hist.sum())
    probabilitas = probabilitas[probabilitas > 0]
    entropi = float(-(probabilitas * np.log2(probabilitas)).sum())

    seg_overlay = asli.copy()
    seg_overlay[masker_produk > 0] = (0, 180, 0)
    seg_overlay = cv2.addWeighted(asli, 0.65, seg_overlay, 0.35, 0)
    kulit_overlay = asli.copy()
    kulit_overlay[daun > 0] = (0, 220, 0)
    kulit_overlay[kulit_aman > 0] = (0, 140, 255)
    kulit_overlay = cv2.addWeighted(asli, 0.6, kulit_overlay, 0.4, 0)

    ringkasan = {
        "mode": "buah",
        "verdict": "CACAT" if busuk else "LULUS",
        "label_verdict": "BUSUK" if busuk else "SEGAR",
        "jumlah_cacat": len(daftar),
        "luas_cacat_persen": round(rasio, 3),
        "luas_cacat_piksel": int(round(luas_busuk)),
        "keparahan": tingkat_keparahan(rasio) if busuk else "-",
        "ambang_terpakai": ambang_persen,
        "ambang_otsu": "-",
        "teks_ambang": f"≥ {ambang_persen}% luas kulit buah",
        "luas_minimum": int(round(luas_min)),
        "sensitivitas": sensitivitas,
        "ukuran": {"lebar": int(lebar), "tinggi": int(tinggi)},
        "rata_rata_intensitas": round(float(abu.mean()), 2),
        "simpangan_baku": round(float(abu.std()), 2),
        "entropi": round(entropi, 3),
        "cakupan_produk_persen": round(cakupan * 100, 1),
        "segmentasi_produk_ok": segmentasi_ok,
        "daftar_cacat": daftar,
    }

    tahapan = {
        "asli": asli,
        "segmentasi": seg_overlay,
        "kulit": kulit_overlay,
        "blackhat": cv2.cvtColor(blackhat, cv2.COLOR_GRAY2BGR),
        "masker": cv2.cvtColor(masker_busuk, cv2.COLOR_GRAY2BGR),
        "hasil": hasil,
    }

    return ringkasan, tahapan
