"""Картинки лендинга из исходников скриншотов 1.6 (AlefBet_Screens/raw_1.6, 1320×2868).
Запуск из website/:  python3 tools/make_images.py
"""
import os
from PIL import Image

SRC = os.path.join(os.path.dirname(__file__), "..", "..", "AlefBet_Screens", "raw_1.6")
OUT = os.path.join(os.path.dirname(__file__), "..", "img", "v16")
W, H = 600, 1304

for lang in ("ru", "en"):
    for name in ("word", "search", "studydark"):
        im = Image.open(os.path.join(SRC, f"{lang}_{name}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
        im.save(os.path.join(OUT, f"{lang}_{name}.webp"), "WEBP", quality=82, method=6)
print("ok")
