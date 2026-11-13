import math

import cv2
import numpy as np


PRESET_SENSITIVITAS = {
    "rendah": {"faktor_ambang": 1.35, "luas_minimum": 260},
    "sedang": {"faktor_ambang": 1.15, "luas_minimum": 120},
    "tinggi": {"faktor_ambang": 0.95, "luas_minimum": 60},
}

BATAS_LULUS_PERSEN = 0.8
UKURAN_KERNEL_MORFOLOGI = 31


def dugaan_jenis(luas, lebar, tinggi, keliling):
    sisi_panjang = max(lebar, tinggi)
    sisi_pendek = max(1, min(lebar, tinggi))
    rasio_aspek = sisi_panjang / sisi_pendek
    if keliling > 0:
        sirkularitas = 4 * math.pi * luas / (keliling * keliling)
    else:
        sirkularitas = 0.0
    if rasio_aspek >= 4.0:
        return "Goresan (scratches)"
    if luas <= 600 and sirkularitas >= 0.45:
        return "Titik / bintik (inclusion / pitted surface)"
    if rasio_aspek >= 2.2:
        return "Retakan halus (crazing)"
    return "Bercak permukaan (patches / rolled-in scale)"


def tingkat_keparahan(rasio_persen):
    if rasio_persen < 3.0:
        return "Ringan"
    if rasio_persen < 10.0:
        return "Sedang"
    return "Berat"


def proses_deteksi(gambar, sensitivitas="sedang", luas_minimum=None):
    preset = PRESET_SENSITIVITAS.get(sensitivitas, PRESET_SENSITIVITAS["sedang"])
    if luas_minimum is None:
        luas_minimum = preset["luas_minimum"]

    if len(gambar.shape) == 2:
        abu = gambar.copy()
        asli = cv2.cvtColor(gambar, cv2.COLOR_GRAY2BGR)
    else:
        asli = gambar.copy()
        abu = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)

    tinggi_img, lebar_img = abu.shape
    total_piksel = float(tinggi_img * lebar_img)

    blur = cv2.GaussianBlur(abu, (5, 5), 0)

    kernel_besar = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (UKURAN_KERNEL_MORFOLOGI, UKURAN_KERNEL_MORFOLOGI)
    )
    blackhat = cv2.morphologyEx(blur, cv2.MORPH_BLACKHAT, kernel_besar)
    tophat = cv2.morphologyEx(blur, cv2.MORPH_TOPHAT, kernel_besar)
    peta_anomali = cv2.addWeighted(blackhat, 1.0, tophat, 1.0, 0)

    ambang_otsu, _ = cv2.threshold(
        peta_anomali, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    ambang = max(8.0, float(ambang_otsu) * preset["faktor_ambang"])
    _, masker_ambang = cv2.threshold(peta_anomali, ambang, 255, cv2.THRESH_BINARY)

    tepi = cv2.Canny(blur, 50, 150)
    kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    tepi_lebar = cv2.dilate(tepi, kernel3, iterations=1)
    _, pendukung_tepi = cv2.threshold(
        peta_anomali, ambang * 0.6, 255, cv2.THRESH_BINARY
    )
    masker_tepi = cv2.bitwise_and(tepi_lebar, pendukung_tepi)

    masker = cv2.bitwise_or(masker_ambang, masker_tepi)
    masker = cv2.morphologyEx(masker, cv2.MORPH_OPEN, kernel3, iterations=1)
    kernel5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    masker = cv2.morphologyEx(masker, cv2.MORPH_CLOSE, kernel5, iterations=1)

    kontur_list, _ = cv2.findContours(
        masker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    kontur_valid = []
    for kontur in kontur_list:
        if cv2.contourArea(kontur) >= luas_minimum:
            kontur_valid.append(kontur)
    kontur_valid.sort(key=cv2.contourArea, reverse=True)

    hasil = asli.copy()
    daftar_cacat = []
    luas_cacat_total = 0.0

    for indeks, kontur in enumerate(kontur_valid, start=1):
        luas = float(cv2.contourArea(kontur))
        keliling = float(cv2.arcLength(kontur, True))
        x, y, w, h = cv2.boundingRect(kontur)
        luas_cacat_total += luas
        daftar_cacat.append(
            {
                "nomor": indeks,
                "jenis_dugaan": dugaan_jenis(luas, w, h, keliling),
                "luas_piksel": int(round(luas)),
                "luas_persen": round(luas / total_piksel * 100, 3),
                "kotak": {"x": int(x), "y": int(y), "lebar": int(w), "tinggi": int(h)},
                "keliling": round(keliling, 1),
            }
        )
        cv2.drawContours(hasil, [kontur], -1, (0, 0, 255), 2)
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

    rasio_persen = luas_cacat_total / total_piksel * 100 if total_piksel else 0.0
    ada_cacat = rasio_persen >= BATAS_LULUS_PERSEN and len(daftar_cacat) > 0

    hist = cv2.calcHist([abu], [0], None, [256], [0, 256]).flatten()
    probabilitas = hist / max(1.0, hist.sum())
    probabilitas = probabilitas[probabilitas > 0]
    entropi = float(-(probabilitas * np.log2(probabilitas)).sum())

    ringkasan = {
        "mode": "baja",
        "verdict": "CACAT" if ada_cacat else "LULUS",
        "label_verdict": "CACAT" if ada_cacat else "LULUS",
        "teks_ambang": f"{round(ambang, 2)} (Otsu {round(float(ambang_otsu), 2)})",
        "jumlah_cacat": len(daftar_cacat),
        "luas_cacat_persen": round(rasio_persen, 3),
        "luas_cacat_piksel": int(round(luas_cacat_total)),
        "keparahan": tingkat_keparahan(rasio_persen) if ada_cacat else "-",
        "ambang_terpakai": round(ambang, 2),
        "ambang_otsu": round(float(ambang_otsu), 2),
        "luas_minimum": int(luas_minimum),
        "sensitivitas": sensitivitas,
        "ukuran": {"lebar": int(lebar_img), "tinggi": int(tinggi_img)},
        "rata_rata_intensitas": round(float(abu.mean()), 2),
        "simpangan_baku": round(float(abu.std()), 2),
        "entropi": round(entropi, 3),
        "daftar_cacat": daftar_cacat,
    }

    tahapan = {
        "asli": asli,
        "grayscale": cv2.cvtColor(abu, cv2.COLOR_GRAY2BGR),
        "blur": cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR),
        "blackhat": cv2.cvtColor(blackhat, cv2.COLOR_GRAY2BGR),
        "tophat": cv2.cvtColor(tophat, cv2.COLOR_GRAY2BGR),
        "peta_anomali": cv2.cvtColor(peta_anomali, cv2.COLOR_GRAY2BGR),
        "masker": cv2.cvtColor(masker, cv2.COLOR_GRAY2BGR),
        "tepi_canny": cv2.cvtColor(tepi, cv2.COLOR_GRAY2BGR),
        "hasil": hasil,
    }

    return ringkasan, tahapan
