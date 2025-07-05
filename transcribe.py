import os
from pathlib import Path
from pydub import AudioSegment
import whisper
import warnings
warnings.filterwarnings("ignore", message="You are using `torch.load` with `weights_only=False`") # igone warning

print("---------- TRANSCRIBING AUDIO ----------")

whisper_model = whisper.load_model("medium")

original_transcribed_path = Path.cwd() / "original_transcribed"
original_transcribed_path.mkdir(exist_ok=True)

audio_chunks_path = Path.cwd() / "audio_chunks"

def trim_audio_to_10s(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    audio = AudioSegment.from_file(file_path)
    trimmed_audio = audio[:10_000]  # 10 seconds in milliseconds
    trimmed_audio.export(file_path, format=file_path.suffix.lstrip('.'))


for file_path in audio_chunks_path.iterdir():
    # Transcribe audio file
    result = whisper_model.transcribe(str(file_path), language="ru", temperature=(0.0, 0.2, 0.4, 0.6, 0.8))
    
    # Save transcription text to a .txt file
    text_output_path = original_transcribed_path / f"{file_path.stem}_transcribed.txt"
    with open(text_output_path, "w", encoding="utf-8") as f:
        f.write(result['text'])

    print(f"Transcribed Text:           File name: {text_output_path.stem}     Text:", result['text'])

    # Trim the original audio chunk
    trim_audio_to_10s(file_path)

print("---------- TRIMMING AUDIO CHUNKS FOR USE AS REFERENCE ----------")