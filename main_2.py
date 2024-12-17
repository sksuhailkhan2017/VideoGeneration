import streamlit as st
import requests
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import os
import google.generativeai as genai
from urllib.parse import quote_plus
import random
import asyncio
import json
import re

# Constants
PEXELS_API_KEY = "WfRAG5IUtSN3kSHJCXJswuGA6MfqQbRnc6ZvxQqi4Z1vXjXSgdCydi2j"
GEMINI_KEY = "AIzaSyCmwU30Y5Y4En8hLIR51710YEKbUIKLMmo"
secs = 10
secs_for_each_clip = 10
number_of_clips_to_merge = secs // secs_for_each_clip

def extract_list_from_text(text):
    """
    Extracts a list of strings from the given text, ignoring Python code block delimiters.

    Args:
        text (str): Input text containing the list.

    Returns:
        list: Extracted list of strings or an empty list if no match is found.
    """
    # Remove Python code block delimiters
    text = re.sub(r'```python|```', '', text).strip()
    
    # Regex to match the list
    pattern = r'\[(?:\s*"([^"]*)"\s*,?)*\]'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # Extract all items within quotes
        items = re.findall(r'"([^"]*)"', match.group())
        return items
    return []

def fetch_stock_footage(instruction):
    encoded_instruction = quote_plus(instruction)  # Encodes spaces as +
    print(encoded_instruction)
    url = f"https://pixabay.com/api/videos/?key=47559207-6a059c5662f5f2564ce2379f2&q={instruction}&orientation=vertical&per_page=5"
    
    headers = {
        "Content-Type": "application/json",  # Set the Content-Type header
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
       
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # Print the error message from the response
    return []

def generate_script_gemini(instruction, brand_name=None, tag_line=None, sale=None, time_spans:list=[]):
    genai.configure(api_key=GEMINI_KEY)

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools='code_execution')
    
    brand_name_desc = f'Brand name is "{brand_name.capitalize()}"' if brand_name else ""
    tag_line_desc = f'Tag line of brand is "{tag_line.capitalize()}"' if tag_line else ""
    sale_desc = f'Our sale is also live.' if sale else ""

    if brand_name_desc or tag_line_desc or sale_desc: other_information = "Other_information: "+", ".join([brand_name_desc,tag_line_desc,sale_desc])
    else: other_information=""

    prompt=f'''Based on the instruction prepare a video ad script that will be displayed over the video as subtitles.
                                      Since I have merged few videos of different time span to make this video, Consider the script to be divided into the repective time-spans in the list:
                                      {str(time_spans)},
                                      
                                      Prepare a script for INSTRUCTION:"General purpose {instruction}".
                                                           {other_information}
                                      
                                      Pattern: [<str>,<str>] make one short sentence of 15 words and another a longer sentence of 50 words for each.
                                      HINT: Based on this generated test we are going to gather the videos so just keep it general and try to observe the information from the INSTRUCTION itself.
                                      NOTE: Response should be a list of text only. as [[<str>,<str>], [<str>,<str>]...]. Only return this list in python tags.
                                      MAKE SURE TO KEEP EACH TEXT WITHIN 70 CHARACTERS EACH'''
    response = model.generate_content(prompt)
    print(prompt)
    script= extract_list_from_text(response.text)
    return (script, response.text)

async def filter_videos_by_resolution(payload, width, height, limit=1):
    selected_videos = []
    
    for hit in payload.get("hits", []):
        for quality, video in hit.get("videos", {}).items():
            if video.get("width") == width and video.get("height") == height:
                selected_videos.append({
                    "id": hit.get("id"),
                    "type": hit.get("type"),
                    "duration": hit.get("duration"),
                    "pageURL": hit.get("pageURL"),
                    "video_url": video.get("url"),
                    "width": video.get("width"),
                    "height": video.get("height"),
                    "size": video.get("size"),
                    "thumbnail": video.get("thumbnail"),
                })
    
    return selected_videos[:limit]

# clipping of the video
def create_video_clips(video_data, output_folder="clips", clip_duration=5, random_choice=False, number_of_clips=1):
    """
    Creates clips from the given video data and saves them in the output folder.

    Args:
        video_data (list): List of video details with their URLs and metadata.
        output_folder (str): Folder where clips will be saved.
        clip_duration (int): Duration of each clip in seconds.
        random_choice (bool): Whether to generate clips randomly.
        number_of_clips (int): Number of clips to create for each video.

    Returns:
        dict: JSON object with paths of the main videos and their clips.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    result = []

    for video in video_data:
        video_url = video.get("video_url")
        video_id = video.get("id")

        # Define paths
        main_video_path = os.path.join(output_folder, f"{video_id}_main.mp4")
        clips_folder = os.path.join(output_folder, f"{video_id}_clips")
        os.makedirs(clips_folder, exist_ok=True)

        try:
            # Load the video
            print(f"Downloading video {video_url}...")
            video_clip = VideoFileClip(video_url)

            # Save the main video locally
            video_clip.write_videofile(main_video_path, codec="libx264")

            # Video duration
            duration = video_clip.duration
            if duration <= clip_duration:
                print(f"Video {video_url} is too short for clipping. Skipping...")
                continue

            clips = []

            if random_choice:
                # Generate `number_of_clips` randomly
                for _ in range(number_of_clips):
                    max_start_time = max(0, duration - clip_duration)
                    start_time = random.uniform(0, max_start_time)
                    end_time = min(start_time + clip_duration, duration)

                    clip_path = os.path.join(clips_folder, f"{video_id}_clip_{int(start_time)}_{int(end_time)}.mp4")
                    subclip = video_clip.subclipped(start_time, end_time)
                    subclip.write_videofile(clip_path, codec="libx264")
                    clips.append(clip_path)

            else:
                # Generate `number_of_clips` symmetrically
                partition_size = duration / number_of_clips
                for i in range(number_of_clips):
                    start_time = i * partition_size
                    end_time = min(start_time + clip_duration, duration)

                    clip_path = os.path.join(clips_folder, f"{video_id}_clip_{int(start_time)}_{int(end_time)}.mp4")
                    subclip = video_clip.subclipped(start_time, end_time)
                    subclip.write_videofile(clip_path, codec="libx264")
                    clips.append(clip_path)

            # Append result
            result.append({
                "main_video": main_video_path,
                "clips": clips
            })

            # Close the video clip
            video_clip.close()

        except Exception as e:
            print(f"Error processing video {video_url}: {e}")

    return result

if __name__=="__main__":

    gemini_response, raw = generate_script_gemini(instruction="ads for employee monitoring system softwares", brand_name="EMP Monitor", tag_line="Time matters", sale=True,time_spans=[secs_for_each_clip for i in range(number_of_clips_to_merge)])

    print(gemini_response)
    print("Gemini responses: ", len(gemini_response))

    clips_and_caption=[]
    for ind, text in enumerate(gemini_response):
        try:
            if text and text.strip()!="":
                video_raw_from_pixabay=fetch_stock_footage(text)
                open(f"fetched_videos_{ind}.json", "w").write(json.dumps(video_raw_from_pixabay))
                if video_raw_from_pixabay!=[]:
                    filtered_videos = asyncio.run(filter_videos_by_resolution(payload=video_raw_from_pixabay, width=1280, height=720, limit=1))
                    if filtered_videos!=[]:
                        vid_clips_output = create_video_clips(filtered_videos, output_folder="clips", clip_duration=5, random_choice=True, number_of_clips=1)
                        if vid_clips_output!=[]:
                            clips_and_caption.append({"clip":vid_clips_output[0]["clips"], "caption":text})
        except Exception as e:
            print(e)
            continue
        
    open(f"clips_and_captions.json", "w").write(json.dumps(clips_and_caption))
    print(clips_and_caption)