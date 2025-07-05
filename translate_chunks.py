import os
from pathlib import Path
import requests
from deep_translator import GoogleTranslator

print("---------- TRANSLATING TEXT ----------")

original_transcribed_path = Path.cwd() / "original_transcribed"
translated_transcribed_path = Path.cwd() / "translated_transcribed"
translated_transcribed_path.mkdir(exist_ok=True)

def translate(text, source="ru", target="en"):
    translated = GoogleTranslator(source=source, target=target).translate(text) # For best results, use GoogleTranslator or DeeplTranslator (requires api_key)

    return str(translated)


for transcribed_chunk_path in original_transcribed_path.iterdir():
    with open(transcribed_chunk_path, "r", encoding="utf-8") as f:
        text = f.read()

    translated_text = translate(text)

    file_path = translated_transcribed_path / str(transcribed_chunk_path.stem + ".txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(translated_text)