import os
import sys
import urllib.request
import zipfile

URL_DATASET = "https://www.kaggle.com/api/v1/datasets/download/kaustubhdikshit/neu-surface-defect-database"
FOLDER_DATASET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset"
)


def main():
    tujuan_zip = os.path.join(FOLDER_DATASET, "neu-surface-defect-database.zip")
    folder_hasil = os.path.join(FOLDER_DATASET, "NEU-DET")
    if os.path.isdir(folder_hasil):
        print("Dataset sudah ada di:", folder_hasil)
        return
    os.makedirs(FOLDER_DATASET, exist_ok=True)
    print("Mengunduh dataset NEU dari Kaggle (sekitar 27 MB)...")
    try:
        urllib.request.urlretrieve(URL_DATASET, tujuan_zip)
    except Exception as galat:
        print("Unduhan otomatis gagal:", galat)
        print("Unduh manual dari: https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database")
        print("Lalu ekstrak isinya ke folder dataset/ sampai muncul folder NEU-DET/.")
        sys.exit(1)
    print("Mengekstrak...")
    with zipfile.ZipFile(tujuan_zip) as arsip:
        arsip.extractall(FOLDER_DATASET)
    os.remove(tujuan_zip)
    print("Selesai. Dataset siap di:", folder_hasil)
    print("Struktur: NEU-DET/train/images/<kelas>/*.jpg dan NEU-DET/validation/images/<kelas>/*.jpg")
    print("Anotasi kotak ground truth ada di NEU-DET/train/annotations/*.xml dan NEU-DET/validation/annotations/*.xml")


if __name__ == "__main__":
    main()
