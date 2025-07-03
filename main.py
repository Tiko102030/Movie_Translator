import subprocess
import os
from pathlib import Path
import shutil
import glob
from pydub import AudioSegment

input_path = Path("C:\Python Projects\Movie_Translator\Input Movie")

def run_demucs(input_file):
    cmd = [
        "demucs",
        "--device", "cuda",
        "-n", "hdemucs_mmi",
        "--shifts", "15",
        "--overlap", "0.5",
        "--float32",
        input_file
    ]
    subprocess.run(cmd, check=True)


def separate_vocals(file):
    """
    """













for file_path in input_path.iterdir():
    subprocess.run(["ffmpeg", "-i", file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", "input.wav"]) # turns the input video file to and audio .wav file 

    vocals_only_path = Path.cwd() / "vocals_only"
    vocals_only_path.mkdir(exist_ok=True)

    shutil.move("input.wav", vocals_only_path)



