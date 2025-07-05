import subprocess
import requests
import os
import sys
from pathlib import Path
import shutil
import glob
from pydub import AudioSegment
import csv

print("---------- MOVIE TRANSLATOR STARTED ----------")

input_path = Path("C:\Python Projects\Movie_Translator\Input_Movies")

def clear_previous_attemps():
    if os.path.exists("audio_chunks"):
        shutil.rmtree("audio_chunks")
    if os.path.exists("vocals_only"):
        shutil.rmtree("vocals_only")
    if os.path.exists("separated"):
        shutil.rmtree("separated")
    if os.path.exists("original_transcribed"):
        shutil.rmtree("original_transcribed")
    if os.path.exists("translated_transcribed"):
        shutil.rmtree("translated_transcribed")
    if os.path.exists("tts_results"):
        shutil.rmtree("tts_results")
    
    if os.path.exists("chunk_times.csv"):
        os.remove("chunk_times.csv")
    if os.path.exists("final_combined.wav"):
        os.remove("final_combined.wav")

def check_f5tts_running(url="http://127.0.0.1:7860/"):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print("✔ F5-TTS is running.")
        else:
            print(f"⚠ F5-TTS returned status code: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ F5-TTS is not running at", url)
        sys.exit(1)

check_f5tts_running()

def run_demucs(input_file):
    cmd = [
        "demucs",
        "--device", "cuda",
        "-n", "hdemucs_mmi",
        "--shifts", "15",     # Uncomment this line for best quality, comment out for fastest
        "--overlap", "0.5",
        "--float32",
        input_file
    ]
    subprocess.run(cmd, check=True)

def move_file(input_folder_path, target_folder_path):
    """
    This will move the *vocals.wav* file into another folder
    \n
    *input_folder_path*: the folder path with the files that need to be moved \n
    *target_folder_path*: the folder where the files will be put into
    """

    for file_path in Path(input_folder_path).iterdir():
        if file_path.name == "vocals.wav":
            shutil.move(file_path, target_folder_path)


def separate_vocals(file, vocals_only_path):
    """
    Seperates the vocals from all the other audio, 
    and moves the speech to the *vocals_only* folder. 
    """
    run_demucs(file)

    separated_folder = Path.cwd() / "separated" / "hdemucs_mmi" / "input"
    move_file(separated_folder, vocals_only_path)

def replace_movie_audio(video_path, new_audio_path, output_path):
    subprocess.run([
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i", str(video_path),          # input video
        "-i", str(new_audio_path),      # new audio file
        "-map", "0:v:0",                # use video from first input
        "-map", "1:a:0",                # use audio from second input
        "-c:v", "copy",                 # copy video stream (no re-encoding)
        "-shortest",                    # trim to the shortest of video/audio
        str(output_path)
    ])


for file_path in input_path.iterdir():
    clear_previous_attemps()

    subprocess.run(["ffmpeg", "-i", file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", "input.wav"]) # turns the input video file to audio .wav file 

    vocals_only_path = Path.cwd() / "vocals_only"
    vocals_only_path.mkdir(exist_ok=True) # creates the folder

    shutil.move("input.wav", vocals_only_path)

    separate_vocals(vocals_only_path / "input.wav", vocals_only_path)

    os.remove(Path.cwd() / vocals_only_path / "input.wav")

    subprocess.run(["python", "splitter.py"])
    subprocess.run(["python", "silent_chunk_remover.py"])
    subprocess.run(["python", "transcribe.py"])
    subprocess.run(["python", "translate_chunks.py"])
    subprocess.run(["python", "translated_tts.py"])
    subprocess.run(["python", "create_sfx.py"])
    subprocess.run(["python", "combine_chunks.py"])

    replace_movie_audio(file_path, str(Path.cwd() / "final_combined.wav"), str(Path.cwd() / "output" / str(file_path.name)))