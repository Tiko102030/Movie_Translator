import os
from pathlib import Path
from pydub import AudioSegment
import shutil

print("---------- COMBINING NON-VOCAL AUDIO ----------")

files_path = Path.cwd() / "separated" / "hdemucs_mmi" / "input"

files_to_combine = ["bass.wav", "drums.wav", "other.wav"]
base = AudioSegment.silent(duration=0)

for file in files_to_combine:
    audio = AudioSegment.from_wav(files_path / file)
    if len(audio) < len(base):
        audio += AudioSegment.silent(duration=len(base) - len(audio))
    else:
        base += AudioSegment.silent(duration=len(audio) - len(base))
    base = base.overlay(audio)

base.export("sfx.wav", format="wav")
shutil.move("sfx.wav", files_path)

for file in files_to_combine:
    # os.remove(files_path / file)
    print("Removed", str(files_path / file))