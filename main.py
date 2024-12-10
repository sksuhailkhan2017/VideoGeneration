import streamlit as st
import requests
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import os
import google.generativeai as genai
from urllib.parse import quote_plus

# Constants
PEXELS_API_KEY = "WfRAG5IUtSN3kSHJCXJswuGA6MfqQbRnc6ZvxQqi4Z1vXjXSgdCydi2j"



def generate_script_gemini(prompt):
    genai.configure(api_key="AIzaSyCmwU30Y5Y4En8hLIR51710YEKbUIKLMmo")

    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        tools='code_execution')

    response = model.generate_content(f'write 100 words on this topic : {prompt}')

    return response.text

def fetch_stock_footage(prompt):
    encoded_prompt = quote_plus(prompt)  # Encodes spaces as +
    print(encoded_prompt)
    url = f"https://pixabay.com/api/videos/?key=47559207-6a059c5662f5f2564ce2379f2&q={encoded_prompt}&orientation=vertical&per_page=5"
    
    headers = {
        "Content-Type": "application/json",  # Set the Content-Type header
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
       
        return [video['videos']["small"]["url"] for video in response.json().get('hits', [])]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # Print the error message from the response
    return []


def create_video_with_captions(video_links, script_text, output_file):
    try:
        clips = []
        captions = script_text.split('.')
        for idx, video_link in enumerate(video_links):
            clip = VideoFileClip(video_link).subclipped(0, 5)  # Use only first 5 seconds

            if idx < len(captions):
                caption = TextClip(text=captions[idx], font="calibri",font_size=72, color='white', bg_color='black',duration=clip.duration,horizontal_align="center",vertical_align="bottom")
                # caption = caption.set_duration(clip.duration).set_position(('center', 'bottom'))
                clip = CompositeVideoClip([clip, caption])
            clips.append(clip)

        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_file, codec="libx264", fps=24)
        return output_file
    except Exception as e:
        st.error(f"Error creating video: {e}")
        return None

# Streamlit UI
st.title("AI-Powered Video Generator")
st.write("Create videos by providing a simple prompt. This app fetches stock footage, generates a script, and compiles the final video.")

prompt = st.text_input("Enter your prompt:", placeholder="E.g., A serene mountain scene with inspirational quotes")

if st.button("Generate Video"):
    if not prompt:
        st.error("Please enter a prompt.")
    else:
        with st.spinner("Generating script..."):
            script = str(generate_script_gemini(prompt))
        if script:
            st.success("Script generated successfully!")
            st.write("### Generated Script:")
            st.write(script)

            with st.spinner("Fetching stock footage..."):
                video_links = fetch_stock_footage(prompt)

            if video_links:
                st.success("Stock footage fetched successfully!")
                st.write("### Video Clips:")
                for link in video_links:
                    st.write(link)

                with st.spinner("Creating video..."):
                    output_video = "output_video.mp4"
                    video_path = create_video_with_captions(video_links, script, output_video)

                if video_path:
                    st.success("Video created successfully!")
                    st.video(video_path)
                else:
                    st.error("Failed to create video.")
            else:
                st.error("No stock footage found for the given prompt.")
