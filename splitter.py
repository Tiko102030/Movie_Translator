import collections
import webrtcvad
from pathlib import Path
from pydub import AudioSegment
import shutil
import csv

print("---------- SPLITTING AUDIO INTO CHUNKS ----------")

def frame_generator(frame_duration_ms, audio_bytes, sample_rate):
    frame_size = int(sample_rate * (frame_duration_ms / 1000.0) * 2)  # 16-bit mono
    offset = 0
    while offset + frame_size <= len(audio_bytes):
        yield audio_bytes[offset:offset + frame_size]
        offset += frame_size

def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    start_time = 0
    frame_duration_s = frame_duration_ms / 1000.0

    for i, frame in enumerate(frames):
        is_speech = vad.is_speech(frame, sample_rate)

        if not triggered:
            ring_buffer.append((frame, i))
            if sum(1 for f, _ in ring_buffer if vad.is_speech(f, sample_rate)) > 0.9 * ring_buffer.maxlen:
                triggered = True
                start_time = ring_buffer[0][1] * frame_duration_s
                ring_buffer.clear()
        else:
            ring_buffer.append((frame, i))
            if sum(1 for f, _ in ring_buffer if not vad.is_speech(f, sample_rate)) > 0.9 * ring_buffer.maxlen:
                end_time = (i - num_padding_frames) * frame_duration_s
                yield start_time, end_time
                triggered = False
                ring_buffer.clear()

    if triggered and ring_buffer:
        end_time = ring_buffer[-1][1] * frame_duration_s
        yield start_time, end_time


def write_header_if_missing(filepath):
    if not Path(filepath).exists():
        with open(filepath, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["filename", "start_time_sec", "end_time_sec"])

def append_row(filepath, filename, start, end):
    with open(filepath, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([filename, f"{start:.2f}", f"{end:.2f}"])


# === MAIN ===

input_file = Path.cwd() / "vocals_only" / "vocals.wav"  # Must be mono, 16kHz, 16-bit PCM
audio = AudioSegment.from_wav(input_file)

# Ensure correct format for VAD
audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
audio_bytes = audio.raw_data

# Prepare VAD
sample_rate = 16000
vad = webrtcvad.Vad(2)
frames = list(frame_generator(30, audio_bytes, sample_rate))
segments = list(vad_collector(sample_rate, 30, 300, vad, frames))

csv_path = "chunk_times.csv"
write_header_if_missing(csv_path)

# Ensure audio_chunks directory exists
audio_chunks_dir = Path.cwd() / "audio_chunks"
audio_chunks_dir.mkdir(exist_ok=True)

# Save chunks
for i, (start, end) in enumerate(segments):
    chunk = audio[int(start * 1000):int((end + 0.5) * 1000)]
    output_path = audio_chunks_dir / f"chunk_{i:03d}.wav"
    chunk.export(output_path, format="wav")
    append_row(csv_path, f"chunk_{i:03d}.wav", start, end + 0.5)
    print(f"Saved chunk_{i:03d}.wav [{start:.2f}s - {end + 0.5:.2f}s]")