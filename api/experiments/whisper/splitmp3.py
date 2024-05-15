import os
from pydub import AudioSegment
import whisper
import math
import json
import time

# Configuration
audio_file = "mp3/speech.mp3"  # Path to your original audio file
chunk_length_ms = 10000  # Length of each audio chunk in milliseconds
output_dir = "audio_chunks"  # Directory where audio chunks will be stored
model_size = "small"  # Whisper model size

# Create the output directory if it doesn't already exist
os.makedirs(output_dir, exist_ok=True)

total_start_time = time.time()
# Load the original audio file
audio = AudioSegment.from_mp3(audio_file)

# Split the audio file into chunks
num_chunks = math.ceil(len(audio) / chunk_length_ms)
chunks = []
chunk_start_times = []  # Store start times for each chunk

for i in range(num_chunks):
    start_ms = i * chunk_length_ms
    end_ms = min((i + 1) * chunk_length_ms, len(audio))
    chunk = audio[start_ms:end_ms]
    chunk_file = os.path.join(output_dir, f"chunk_{i + 1}.mp3")
    chunk.export(chunk_file, format="mp3")
    chunks.append(chunk_file)
    chunk_start_times.append(start_ms / 1000.0)  # Convert milliseconds to seconds

# Load the Whisper model
model = whisper.load_model(model_size)

# Function to adjust timestamps based on the chunk's start time
def adjust_timestamps(transcription, start_time):
    for segment in transcription['segments']:
        segment['start'] += start_time
        segment['end'] += start_time
        for word in segment.get('words', []):
            word['start'] += start_time
            word['end'] += start_time

# Open a single text file to compile all transcriptions
compiled_transcription_txt = os.path.join("text", "compiled_transcriptions.txt")
with open(compiled_transcription_txt, 'w') as compiled_txt_file:

    # Transcribe each chunk and print the result as it's processed
    all_transcriptions = []  # Store all transcriptions to compile them later

    for i, (chunk_file, start_time) in enumerate(zip(chunks, chunk_start_times), start=1):
        print(f"Transcribing chunk {i}/{len(chunks)} starting at {start_time} seconds...")
        result = model.transcribe(chunk_file)
        adjust_timestamps(result, start_time)  # Adjust timestamps based on the chunk's actual start time
        all_transcriptions.append(result)  # Append adjusted transcription to the list

        # Write the transcription text to the compiled text file without "Chunk X transcription"
        compiled_txt_file.write(f"{result['text']}\n\n")  # Removed the chunk counter from the text file

        # Optional: Save each adjusted transcription to a separate JSON file for subtitles
        with open(os.path.join(output_dir, f"subtitles_{i}.json"), "w") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)

    # Optionally, save all transcriptions into a single JSON file
    with open(os.path.join(output_dir, "compiled_transcriptions.json"), "w") as json_file:
        json.dump(all_transcriptions, json_file, ensure_ascii=False, indent=4)

total_end_time = time.time()
print(f"Time: {total_end_time - total_start_time} seconds")