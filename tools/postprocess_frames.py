#!/usr/bin/env python3
"""Пост-обработка кадров «Я не в сети».
- Кроп 1344x768 (1.75:1) -> 16:9, апскейл до 3840x2160 (для плавного zoompan)
- Плюс веб-миниатюры 672x378 для сайта
"""
from PIL import Image, ImageEnhance
import os

SRC = "/home/z/my-project/dirtygen/frames"
DST = "/home/z/my-project/dirtygen/frames_4k"
WEB = "/home/z/my-project/dirtygen/assets/frames_web"
os.makedirs(DST, exist_ok=True)
os.makedirs(WEB, exist_ok=True)

TW, TH = 3840, 2160

def crop_169(img):
    w, h = img.size
    target_ratio = 16 / 9
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        return img.crop((x0, 0, x0 + new_w, h))
    new_h = int(w / target_ratio)
    y0 = (h - new_h) // 2
    return img.crop((0, y0, w, y0 + new_h))

count = 0
for name in sorted(os.listdir(SRC)):
    if not name.endswith(".png"):
        continue
    path = os.path.join(SRC, name)
    img = Image.open(path).convert("RGB")
    img169 = crop_169(img)
    # 4K для видео
    big = img169.resize((TW, TH), Image.LANCZOS)
    big = ImageEnhance.Contrast(big).enhance(1.03)
    big.save(os.path.join(DST, name.replace(".png", ".jpg")), "JPEG", quality=90, optimize=True)
    # веб-миниатюра для сайта
    small = img169.resize((672, 378), Image.LANCZOS)
    small.save(os.path.join(WEB, name.replace(".png", ".jpg")), "JPEG", quality=82, optimize=True)
    count += 1
    print(f"{name}: 4K + web OK")

print(f"DONE: {count} frames")
