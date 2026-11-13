import os

import cv2
import numpy as np


def buat_permukaan_bersih(seed, terang=150):
    rng = np.random.default_rng(seed)
    dasar = np.full((200, 200), float(terang))
    dasar += rng.normal(0, 5, (200, 200))
    garis_giling = np.sin(np.linspace(0, 6, 200)) * 3
    dasar += garis_giling[np.newaxis, :]
    dasar += rng.normal(0, 2, (200, 200))
    img = np.clip(dasar, 0, 255).astype(np.uint8)
    return cv2.GaussianBlur(img, (3, 3), 0)


def main():
    folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "dataset",
        "contoh",
        "normal_sintetis",
    )
    os.makedirs(folder, exist_ok=True)
    for seed, terang in ((1, 150), (2, 165)):
        img = buat_permukaan_bersih(seed, terang)
        tujuan = os.path.join(folder, f"normal_sintetis_{seed}.jpg")
        cv2.imwrite(tujuan, img)
        print("tersimpan:", tujuan)


if __name__ == "__main__":
    main()
