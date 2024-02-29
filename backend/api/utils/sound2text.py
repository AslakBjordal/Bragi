import whisper
import time

def sound2text(file_path, size):
    model = whisper.load_model(size)
    result = model.transcribe(file_path)
    return result["text"]


# test all sizes of the model "tiny", "base", "small", "medium", "large"
def test_all_sizes():
    file_path = "mp3/speech.mp3"
    for size in ["tiny", "base", "small", "medium", "large"]:
        print(f"Size: {size}")
        result = sound2text(file_path, size)
        # write the result to a dictionary called result to a file named 'test_tiny.txt''test_base.txt''test_small.txt''test_medium.txt''test_large.txt'
        with open(f"text/test_{size}.txt", "w") as file:
            file.write(result)


if __name__ == "__main__":
    start_time = time.time()  
    test_all_sizes()
    end_time = time.time()  
    print(f"Time: {end_time - start_time} seconds")