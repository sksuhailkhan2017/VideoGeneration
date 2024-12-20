import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import json

def generate_timed_captions(audio_filename, model_size="base"):
    # Load the Whisper model
    WHISPER_MODEL = load_model(model_size)
   
    # Transcribe the audio with word-level timestamps
    gen = transcribe_timestamped(
        WHISPER_MODEL, 
        audio_filename, 
        verbose=False, 
        fp16=False,
        compute_word_confidence=True,  # Ensures word-level confidence
        remove_punctuation_from_words=True  # Removes punctuation for better splitting
    )
   
    return get_captions_with_time(gen)

def split_words_by_size(words, max_caption_size):
    # Split words into smaller captions with a max size
    half_caption_size = max_caption_size / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= max_caption_size:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= half_caption_size and words:
                break
        captions.append(caption)
    return captions

def get_timestamp_mapping(whisper_analysis):
    # Map word positions to their end timestamps
    index = 0
    location_to_timestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            new_index = index + len(word['text']) + 1
            location_to_timestamp[(index, new_index)] = word['end']
            index = new_index
    return location_to_timestamp

def clean_word(word):
    # Remove unwanted characters
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolate_time_from_dict(word_position, timestamp_mapping):
    # Interpolate timestamps for a given word position
    for key, value in timestamp_mapping.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def get_captions_with_time(whisper_analysis, max_caption_size=15, consider_punctuation=False):
    # Generate captions with timestamps
    word_location_to_time = get_timestamp_mapping(whisper_analysis)
    position = 0
    start_time = 0
    captions_pairs = []
    text = whisper_analysis['text']
    
    if consider_punctuation:
        sentences = re.split(r'(?<=[.!?]) +', text)
        words = [word for sentence in sentences for word in split_words_by_size(sentence.split(), max_caption_size)]
    else:
        words = text.split()
        words = [clean_word(word) for word in split_words_by_size(words, max_caption_size)]
    
    for word in words:
        position += len(word) + 1
        end_time = interpolate_time_from_dict(position, word_location_to_time)
        if end_time and word:
            captions_pairs.append(((start_time, end_time), word))
            start_time = end_time
    
    # Print captions with timestamps
    captions_timed_dict=[]

    for (start, end), caption in captions_pairs:
        object={
            "start_time":float(start),
            "end_time":float(end),
            "caption":caption,
        }
        captions_timed_dict.append(object)

    return captions_timed_dict

# def sample_object():
#     sample=[{'start_time': 0.0, 'end_time': 0.74, 'caption': 'Step up your'}, {'start_time': 0.74, 'end_time': 1.32, 'caption': 'style game'}, {'start_time': 1.32, 'end_time': 2.0, 'caption': 'with Astris'}, {'start_time': 2.0, 'end_time': 2.52, 'caption': 'to Farny'}, {'start_time': 2.52, 'end_time': 4.06, 'caption': 'Astrisk Your'}, {'start_time': 4.06, 'end_time': 4.4, 'caption': 'ultimate'}, {'start_time': 4.4, 'end_time': 5.3, 'caption': 'destination for'}, {'start_time': 5.3, 'end_time': 6.0, 'caption': 't-shirts that'}, {'start_time': 6.0, 'end_time': 6.64, 'caption': 'blend comfort'}, {'start_time': 6.64, 'end_time': 7.62, 'caption': 'attitude and'}, {'start_time': 7.62, 'end_time': 8.52, 'caption': 'individuality'}, {'start_time': 8.52, 'end_time': 9.9, 'caption': 'From bold'}, {'start_time': 9.9, 'end_time': 10.5, 'caption': 'graphics to'}, {'start_time': 10.5, 'end_time': 10.8, 'caption': 'minimalist'}, {'start_time': 10.8, 'end_time': 11.64, 'caption': "quotes we've"}, {'start_time': 11.64, 'end_time': 12.22, 'caption': 'got the perfect'}, {'start_time': 12.22, 'end_time': 12.9, 'caption': 'designs to'}, {'start_time': 12.9, 'end_time': 13.28, 'caption': 'match your'}, {'start_time': 13.28, 'end_time': 14.84, 'caption': 'vibe Whether'}, {'start_time': 14.84, 'end_time': 15.3, 'caption': "you're hitting"}, {'start_time': 15.3, 'end_time': 15.78, 'caption': 'the streets'}, {'start_time': 15.78, 'end_time': 16.46, 'caption': 'chilling at'}, {'start_time': 16.46, 'end_time': 17.24, 'caption': 'home or making'}, {'start_time': 17.24, 'end_time': 17.78, 'caption': 'a statement'}, {'start_time': 17.78, 'end_time': 18.82, 'caption': 'Astris Chodia'}, {'start_time': 18.82, 'end_time': 19.54, 'caption': 'Astrisk lets'}, {'start_time': 19.54, 'end_time': 20.08, 'caption': 'you express'}, {'start_time': 20.08, 'end_time': 20.84, 'caption': 'yourself like'}, {'start_time': 20.84, 'end_time': 21.46, 'caption': 'never before'}, {'start_time': 21.46, 'end_time': 23.18, 'caption': 'So why wait'}, {'start_time': 23.18, 'end_time': 24.56, 'caption': 'Live your'}, {'start_time': 24.56, 'end_time': 25.14, 'caption': 'vibe where'}, {'start_time': 25.14, 'end_time': 25.72, 'caption': "you're attitude"}, {'start_time': 25.72, 'end_time': 26.38, 'caption': 'and own your'}, {'start_time': 26.38, 'end_time': 26.92, 'caption': 'style with'}, {'start_time': 26.92, 'end_time': 27.78, 'caption': 'Astris Chodia'}, {'start_time': 27.78, 'end_time': 29.4, 'caption': 'Astrisk Shop'}, {'start_time': 29.4, 'end_time': 30.0, 'caption': 'now and let'}, {'start_time': 30.0, 'end_time': 30.62, 'caption': 'your t-shirt'}, {'start_time': 30.62, 'end_time': 31.28, 'caption': 'do the talking'}]
#     return sample


if __name__ == "__main__":
    # Path to the audio file
    audio_file = "audio.mp3"  # Replace with your audio file path
    
    # Generate timed captions
    captions = generate_timed_captions(audio_file, model_size="base")
    print(type(captions), captions)
    with open("sample_timed_scripts.json", "w") as f:
        json.dump(captions, f)

