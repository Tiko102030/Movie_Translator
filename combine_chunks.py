import csv
from pathlib import Path
from pydub import AudioSegment

print("---------- APPLYING TRANSLATED CHUNKS ONTO BASE AUDIO ----------")

base_audio = AudioSegment.from_wav(str(Path.cwd() / "separated" / "hdemucs_mmi" / "input" / "sfx.wav"))
output_audio = base_audio

csv_path = Path("chunk_times.csv")
chunks_folder = Path("tts_results")  

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        filename = row["filename"]
        start_time_ms = int(float(row["start_time_sec"]) * 1000)
        
        chunk_path = chunks_folder / filename
        if not chunk_path.exists():
            print(f"⚠️ Missing chunk: {filename}")
            continue

        chunk = AudioSegment.from_wav(chunk_path)

        # Overlay chunk at the correct position
        output_audio = output_audio.overlay(chunk, position=start_time_ms)

# Save the result
output_audio.export("final_combined.wav", format="wav")
