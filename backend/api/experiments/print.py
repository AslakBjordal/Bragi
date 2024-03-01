import json

def print_segment_transcripts_with_timestamps(json_file):
    # Load the JSON data from the file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Check if 'segments' key exists in the data
    if 'segments' in data:
        # Iterate through each segment in the data
        for segment in data['segments']:
            # Extract the full text, start, and end times of the segment
            text = segment.get('text', 'No text available')
            start_time = segment.get('start', 'Unknown start time')
            end_time = segment.get('end', 'Unknown end time')
            segment_id = segment.get('id', 'No ID')

            # Print the segment's text and its timestamps
            print(f"Segment ID: {segment_id} (Start: {start_time}, End: {end_time})\nText: {text}\n")
    else:
        print("No segments data found.")

# Specify the path to your JSON file
json_file_path = 'text/test_small_timestamps.json'
print_segment_transcripts_with_timestamps(json_file_path)

