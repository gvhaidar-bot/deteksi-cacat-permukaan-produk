import argparse
import csv
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

import cv2

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"),
)

from deteksi import proses_deteksi

KELAS = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]


def kotak_ground_truth(path_xml):
    if not os.path.isfile(path_xml):
        return []
    pohon = ET.parse(path_xml)
    hasil = []
    for obj in pohon.getroot().iter("object"):
        bb = obj.find("bndbox")
        hasil.append(
            tuple(int(bb.find(k).text) for k in ("xmin", "ymin", "xmax", "ymax"))
        )
    return hasil


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    antar = (x2 - x1) * (y2 - y1)
    luas_a = (a[2] - a[0]) * (a[3] - a[1])
    luas_b = (b[2] - b[0]) * (b[3] - b[1])
    return antar / max(1, luas_a + luas_b - antar)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--sensitivitas", default="sedang")
    parser.add_argument("--maks-per-kelas", type=int, default=0)
    argumen = parser.parse_args()

    folder_gambar = os.path.join(argumen.folder, "images")
    folder_anotasi = os.path.join(argumen.folder, "annotations")
    if not os.path.isdir(folder_gambar):
        print("Folder images tidak ditemukan di:", argumen.folder)
        print("Contoh pemakaian: python scripts/evaluasi.py --folder dataset/NEU-DET/validation")
        sys.exit(1)

    baris = []
    total_citra = 0
    total_terdeteksi = 0
    total_gt = 0
    total_gt_kena = 0

    for kelas in KELAS:
        berkas = sorted(glob.glob(os.path.join(folder_gambar, kelas, "*.jpg")))
        if argumen.maks_per_kelas > 0:
            berkas = berkas[: argumen.maks_per_kelas]
        terdeteksi = 0
        gt_kena = 0
        gt_jumlah = 0
        rasio_total = 0.0
        for path in berkas:
            gambar = cv2.imread(path)
            if gambar is None:
                continue
            ringkasan, _ = proses_deteksi(gambar, sensitivitas=argumen.sensitivitas)
            rasio_total += ringkasan["luas_cacat_persen"]
            if ringkasan["verdict"] == "CACAT":
                terdeteksi += 1
            nama_xml = os.path.splitext(os.path.basename(path))[0] + ".xml"
            prediksi = [
                (
                    c["kotak"]["x"],
                    c["kotak"]["y"],
                    c["kotak"]["x"] + c["kotak"]["lebar"],
                    c["kotak"]["y"] + c["kotak"]["tinggi"],
                )
                for c in ringkasan["daftar_cacat"]
            ]
            for gt in kotak_ground_truth(os.path.join(folder_anotasi, nama_xml)):
                gt_jumlah += 1
                if any(iou(gt, p) >= 0.10 for p in prediksi):
                    gt_kena += 1
        jumlah = len(berkas)
        baris.append(
            {
                "kelas": kelas,
                "jumlah_citra": jumlah,
                "citra_terdeteksi_cacat": terdeteksi,
                "tingkat_deteksi_persen": round(terdeteksi / jumlah * 100, 1) if jumlah else 0.0,
                "kotak_ground_truth": gt_jumlah,
                "kotak_terlokalisasi": gt_kena,
                "tingkat_lokalisasi_persen": round(gt_kena / gt_jumlah * 100, 1) if gt_jumlah else 0.0,
                "rata_rata_luas_cacat_persen": round(rasio_total / jumlah, 2) if jumlah else 0.0,
            }
        )
        total_citra += jumlah
        total_terdeteksi += terdeteksi
        total_gt += gt_jumlah
        total_gt_kena += gt_kena

    ringkasan_total = {
        "folder": argumen.folder,
        "sensitivitas": argumen.sensitivitas,
        "jumlah_citra": total_citra,
        "citra_terdeteksi_cacat": total_terdeteksi,
        "tingkat_deteksi_persen": round(total_terdeteksi / total_citra * 100, 1) if total_citra else 0.0,
        "kotak_ground_truth": total_gt,
        "kotak_terlokalisasi": total_gt_kena,
        "tingkat_lokalisasi_persen": round(total_gt_kena / total_gt * 100, 1) if total_gt else 0.0,
        "per_kelas": baris,
    }

    print(f"{'Kelas':18s} {'Deteksi':>10s} {'Lokalisasi GT':>15s} {'Rata2 Luas':>12s}")
    for b in baris:
        print(
            f"{b['kelas']:18s} {b['citra_terdeteksi_cacat']:4d}/{b['jumlah_citra']:<5d} "
            f"{b['kotak_terlokalisasi']:5d}/{b['kotak_ground_truth']:<9d} "
            f"{b['rata_rata_luas_cacat_persen']:10.2f} %"
        )
    print(
        f"{'TOTAL':18s} {total_terdeteksi:4d}/{total_citra:<5d} "
        f"{total_gt_kena:5d}/{total_gt:<9d}"
    )
    print(f"Tingkat deteksi citra : {ringkasan_total['tingkat_deteksi_persen']} %")
    print(f"Tingkat lokalisasi GT : {ringkasan_total['tingkat_lokalisasi_persen']} % (IoU >= 0,10)")

    folder_keluaran = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hasil_evaluasi"
    )
    os.makedirs(folder_keluaran, exist_ok=True)
    with open(os.path.join(folder_keluaran, "hasil_evaluasi.json"), "w", encoding="utf-8") as f:
        json.dump(ringkasan_total, f, indent=2, ensure_ascii=False)
    with open(os.path.join(folder_keluaran, "hasil_evaluasi.csv"), "w", newline="", encoding="utf-8") as f:
        penulis = csv.DictWriter(f, fieldnames=list(baris[0].keys()))
        penulis.writeheader()
        penulis.writerows(baris)
    print("Hasil disimpan di folder hasil_evaluasi/ (JSON + CSV)")


if __name__ == "__main__":
    main()
