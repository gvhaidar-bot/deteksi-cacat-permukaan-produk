import base64
import os

import cv2
import numpy as np
from flask import Flask, jsonify, request, send_from_directory

from deteksi import proses_deteksi

DASAR = os.path.dirname(os.path.abspath(__file__))
FOLDER_FRONTEND = os.path.join(DASAR, "..", "frontend")
FOLDER_CONTOH = os.path.join(DASAR, "..", "dataset", "contoh")
EKSTENSI_DIIZINKAN = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
UKURAN_MAKS_BYTE = 10 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = UKURAN_MAKS_BYTE


def gambar_ke_base64(gambar):
    sukses, buffer = cv2.imencode(".jpg", gambar, [cv2.IMWRITE_JPEG_QUALITY, 88])
    if not sukses:
        return None
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")


def jalankan_deteksi(gambar, formulir):
    sensitivitas = formulir.get("sensitivitas", "sedang")
    if sensitivitas not in ("rendah", "sedang", "tinggi"):
        sensitivitas = "sedang"
    luas_mentah = formulir.get("luas_minimum", "")
    luas_minimum = None
    if str(luas_mentah).strip().isdigit():
        luas_minimum = max(10, min(5000, int(luas_mentah)))
    ringkasan, tahapan = proses_deteksi(gambar, sensitivitas, luas_minimum)
    return {
        "ringkasan": ringkasan,
        "tahapan": {nama: gambar_ke_base64(img) for nama, img in tahapan.items()},
    }


@app.route("/")
def beranda():
    return send_from_directory(FOLDER_FRONTEND, "index.html")


@app.route("/<path:nama_file>")
def aset_frontend(nama_file):
    return send_from_directory(FOLDER_FRONTEND, nama_file)


@app.route("/api/kesehatan")
def kesehatan():
    return jsonify({"status": "ok", "layanan": "deteksi-cacat-permukaan"})


@app.route("/api/contoh")
def daftar_contoh():
    hasil = []
    if os.path.isdir(FOLDER_CONTOH):
        for kelas in sorted(os.listdir(FOLDER_CONTOH)):
            folder_kelas = os.path.join(FOLDER_CONTOH, kelas)
            if not os.path.isdir(folder_kelas):
                continue
            for nama in sorted(os.listdir(folder_kelas)):
                if os.path.splitext(nama)[1].lower() in EKSTENSI_DIIZINKAN:
                    hasil.append(
                        {
                            "kelas": kelas,
                            "nama": nama,
                            "url": f"/api/contoh-file/{kelas}/{nama}",
                        }
                    )
    return jsonify({"contoh": hasil})


@app.route("/api/contoh-file/<kelas>/<nama>")
def berkas_contoh(kelas, nama):
    folder = os.path.join(FOLDER_CONTOH, kelas)
    return send_from_directory(folder, nama)


@app.route("/api/deteksi", methods=["POST"])
def deteksi_unggahan():
    if "gambar" not in request.files:
        return jsonify({"galat": "Berkas gambar tidak ditemukan pada permintaan."}), 400
    berkas = request.files["gambar"]
    if not berkas.filename:
        return jsonify({"galat": "Nama berkas kosong."}), 400
    ekstensi = os.path.splitext(berkas.filename)[1].lower()
    if ekstensi not in EKSTENSI_DIIZINKAN:
        return jsonify({"galat": "Format berkas tidak didukung. Gunakan JPG, PNG, BMP, atau WebP."}), 400
    data = berkas.read()
    if not data:
        return jsonify({"galat": "Berkas kosong."}), 400
    gambar = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if gambar is None:
        return jsonify({"galat": "Berkas tidak dapat dibaca sebagai gambar."}), 400
    return jsonify(jalankan_deteksi(gambar, request.form))


@app.route("/api/deteksi-contoh", methods=["POST"])
def deteksi_contoh():
    isi = request.get_json(silent=True) or {}
    kelas = str(isi.get("kelas", ""))
    nama = str(isi.get("nama", ""))
    if "/" in kelas or "\\" in kelas or "/" in nama or "\\" in nama or ".." in nama:
        return jsonify({"galat": "Nama contoh tidak valid."}), 400
    path = os.path.join(FOLDER_CONTOH, kelas, nama)
    if not os.path.isfile(path):
        return jsonify({"galat": "Contoh tidak ditemukan."}), 404
    gambar = cv2.imread(path, cv2.IMREAD_COLOR)
    if gambar is None:
        return jsonify({"galat": "Contoh tidak dapat dibaca."}), 500
    formulir = {
        "sensitivitas": str(isi.get("sensitivitas", "sedang")),
        "luas_minimum": str(isi.get("luas_minimum", "")),
    }
    return jsonify(jalankan_deteksi(gambar, formulir))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
