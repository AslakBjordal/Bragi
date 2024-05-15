from faster_whisper import WhisperModel
import time

def format_time_srt(seconds):
    # Converts time in seconds to SRT format.
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:06.3f}'.replace('.', ',')

def write_srt_segment(segment, index, filepath):
    # Appends a single segment in SRT format to a file.
    start_time = format_time_srt(segment.start)
    end_time = format_time_srt(segment.end)
    text = segment.text.replace('\n', ' ').strip()  # Replace newlines with spaces
    with open(filepath, 'a') as file:  # Open in append mode
        file.write(f"{index}\n{start_time} --> {end_time}\n{text}\n\n")

# Main transcription process
model_size = "medium"
audio_path = "speech.mp3"
output_path = "output.srt"  # Define the output file path

# Clear or create the file at the beginning of the transcription
with open(output_path, 'w') as f:
    pass  

start_time = time.time()
model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe(audio_path, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# Write each transcribed segment in SRT format to the file as it becomes available
for index, segment in enumerate(segments, start=1):
    write_srt_segment(segment, index, output_path)

end_time = time.time()
print("Time taken: ", end_time - start_time)
