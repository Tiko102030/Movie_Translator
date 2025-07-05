from pydub import AudioSegment
from pathlib import Path
import os
import csv

print("---------- REMOVING SILENT CHUNKS ----------")

audio_chunks_path = Path.cwd() / "audio_chunks"
csv_path = Path.cwd() / "chunk_times.csv"

def is_chunk_silent(path, silence_threshold_db=-40):
    audio = AudioSegment.from_wav(path)
    return audio.dBFS < silence_threshold_db

def is_chunk_silent_advanced(path, rms_threshold=300):
    audio = AudioSegment.from_wav(path)
    return audio.rms < rms_threshold

silent_chunk_names = set()

for chunk_path in audio_chunks_path.iterdir():
    if is_chunk_silent(chunk_path):
        os.remove(chunk_path)
        print(chunk_path.stem, " was blank, removed automatically")
    elif is_chunk_silent_advanced(chunk_path):
        os.remove(chunk_path)
        print(chunk_path.stem, " was blank, removed automatically")


# Rewrite CSV excluding removed chunks
updated_rows = []
with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["filename"] not in silent_chunk_names:
            updated_rows.append(row)

# Overwrite the original CSV
with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["filename", "start_time_sec", "end_time_sec"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)