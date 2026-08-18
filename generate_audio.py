# -*- coding: utf-8 -*-
"""Озвучка слов для alefbet.tech: say -v Carmit → afconvert → audio/w/<id>.m4a.

Файлы ключуются по id слова из Words.json, чтобы слаги страниц могли меняться.
Уже существующие файлы пропускаются — можно перезапускать.

Запуск:  python3 generate_audio.py
"""
import json, os, subprocess, sys, tempfile

WORDS_JSON = os.path.join(os.path.dirname(__file__), "..", "HebrewTranslator", "Words.json")
OUT_DIR = os.path.join(os.path.dirname(__file__), "audio", "w")

def synth(text, out_path):
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        aiff = tmp.name
    try:
        subprocess.run(["say", "-v", "Carmit", "-o", aiff, text], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "32000", aiff, out_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        if os.path.exists(aiff):
            os.remove(aiff)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    words = json.load(open(WORDS_JSON))
    # озвучиваем: все слова A1 (страницы /slovar/) + глаголы A2 (страницы /glagoly/)
    todo = [w for w in words
            if w.get("he") and w.get("id")
            and (w.get("level") == "A1" or (w.get("pos") == "verb" and w.get("level") == "A2"))]
    done = skipped = failed = 0
    for w in todo:
        out = os.path.join(OUT_DIR, f'{w["id"]}.m4a')
        if os.path.exists(out):
            skipped += 1
            continue
        if synth(w["he"], out):
            done += 1
        else:
            failed += 1
        if (done + failed) % 100 == 0:
            print(f"progress: {done} done, {failed} failed, {skipped} skipped", flush=True)
    print(f"audio: {done} generated, {skipped} skipped, {failed} failed, total {len(todo)}")

if __name__ == "__main__":
    main()
