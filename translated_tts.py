import requests
import os
from pathlib import Path
from gradio_client import Client, file
import shutil
import subprocess

print("---------- TURNING TRANSLATED TEXT TO SPEECH ----------")

transcribed_audio_chunks_path = Path.cwd() / "translated_transcribed"
audio_chunks_path = Path.cwd() / "audio_chunks"

client = Client("http://127.0.0.1:7860/")

def make_audio(ref_audio_path, text_to_gen, chunk_name):
    result = client.predict(
        ref_audio_input=file(str(ref_audio_path)),
        ref_text_input="",
        gen_text_input=text_to_gen,
        remove_silence=True,
        randomize_seed=False,
        seed_input=123,
        cross_fade_duration_slider=0.15,
        nfe_slider=40,
        speed_slider=0.8,
        api_name="/basic_tts"
    )

    save_path = Path.cwd() / "tts_results"
    save_path.mkdir(exist_ok=True)
    file_path = save_path / f"{chunk_name}.wav"

    if isinstance(result, tuple):
        audio_path = result[0]
    else:
        audio_path = result

    if isinstance(audio_path, str) and Path(audio_path).exists():
        shutil.copy(audio_path, file_path)
    else:
        raise RuntimeError("Unexpected output from TTS API")

def slow_down_audio_in_place(file_path, factor=0.8):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not (0.5 <= factor <= 2.0):
        raise ValueError("FFmpeg's atempo filter only supports 0.5 to 2.0 per pass")

    temp_path = file_path.with_name(f"{file_path.stem}_temp{file_path.suffix}")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(file_path),
        "-filter:a", f"atempo={factor}",
        str(temp_path)
    ], check=True)

    # Replace original file
    temp_path.replace(file_path)

for transcribed_chunk_path in transcribed_audio_chunks_path.iterdir():
    ref_audio_chunk = audio_chunks_path / (transcribed_chunk_path.stem.removesuffix("_transcribed") + ".wav")
    
    with open(transcribed_chunk_path, "r", encoding="utf-8") as f:
        text_to_speak = f.read().strip()
    
    chunk_name = transcribed_chunk_path.stem.removesuffix("_transcribed")
    make_audio(ref_audio_chunk, text_to_speak, chunk_name)

    tts_result_path = Path.cwd() / "tts_results" / f"{chunk_name}.wav"
    slow_down_audio_in_place(tts_result_path)
