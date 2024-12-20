from script_generator import generate_script # Topic to Script
from audio_generator import generate_audio# Script to Audio
from timed_caption_generator import generate_timed_captions, sample_object  # Audio to Timed Script
from clips_generator import generate_clips # Timed to Clips 
from video_generator import generate_video # Clips to Video 
from caption_generator import generate_caption_on_video # Video to Caption

#----------------------------------------------------------------

def main(topic):
    script=generate_script(topic=topic) # Done
    audio_file=generate_audio(script=script) # Done
    timed_captions=generate_timed_captions(audio_filename=audio_file) # Done
    clips_list=generate_clips(timed_captions=timed_captions) # to be done 
    video_file=generate_video(clips_list=clips_list) # to be done 
    video_file_with_captions=generate_caption_on_video(video_filename=video_file, timed_captions_object=timed_captions)
         # to be done 
    return video_file_with_captions


if __name__=="__main__":
    topic:str="T-shirt selling brand with unique selling proposition as high quality and loose fit design." 
