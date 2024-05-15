import whisper
import time
import json

def sound2text(file_path, size, include_timestamps=False):  # Fixed typo here
    model = whisper.load_model(size)
    result = model.transcribe(file_path, task="transcribe", word_timestamps=include_timestamps)
    return result

# test all sizes of the model "tiny", "base", "small", "medium", 'large-v1', 'large-v2', 'large-v3', 'large' 
def test_all_sizes():
    all_models= [
        "tiny",
        "base", 
        "small", 
        "medium", 
        "large",
        "large-v1", 
        "large-v2",
        "large-v3", 
    ]
    single_model = ["small"]
    file_path = "mp3/speech.mp3"
    for size in single_model:
        print(f"Size: {size}")
        result = sound2text(file_path, size, include_timestamps=True)
        # Write the detailed result including timestamps to a JSON file for better readability
        with open(f"text/test_{size}_timestamps.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    start_time = time.time()  
    test_all_sizes()
    end_time = time.time()  
    print(f"Time: {end_time - start_time} seconds")