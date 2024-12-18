import subprocess
import json
import traceback
import os 
import textwrap

os.makedirs("outputs", exist_ok=True)

# # JSON data with video clips and captions
# data = json.loads(open(".\\logs\\clips_and_captions.json", "r").read())

# Function to apply caption to a video with line wrapping
def add_caption_to_video(input_file, caption, output_file, line_spacing=5, font_size=40, video_width=1280):
    # Approximate max characters per line for 1280p width
    max_characters_per_line = video_width // (font_size // 2)

    # Wrap the text into multiple lines
    wrapped_lines = textwrap.wrap(caption, width=max_characters_per_line)

    # Write wrapped lines to a text file with LF endings
    text_file = "text_.txt"
    try:
        with open(text_file, "w", encoding="utf-8", newline="\n") as f:
            for line in wrapped_lines:
                f.write(line + "\n")
        print(f"Wrapped text written to {text_file}")
    except Exception as e:
        print(f"Error writing to text file: {e}")
        return

    # Calculate y-coordinate dynamically for multi-line text
    total_line_height = font_size * len(wrapped_lines) + (line_spacing * (len(wrapped_lines) - 1))
    y_position = f"h-{total_line_height + 50}"  # Bottom margin with padding

    # FFmpeg command to overlay text from the file
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
               f"textfile={text_file}:fontcolor=#ffffff:borderw=1:bordercolor=black:"
               f"fontsize={font_size}:line_spacing={line_spacing}:"
               f"x=50:y={y_position}",
        "-codec:a", "copy",
        output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(traceback.format_exc())
        print(f"Error occurred while processing {input_file}: {e}")


def merge_all_clips(data):
    # List to hold the names of processed video files
    processed_videos = []

    # Process each clip and add its caption
    for idx, item in enumerate(data):
        print("\n\nidx", idx, "item", item, "\n\n")
        try:
            input_file = item["clip"][0]
            caption = item["caption"]
            caption=caption.replace(":", "")
            output_file = f".\\outputs\\output_video_{idx+1}.mp4"
            print(">>>",type(output_file), output_file)
            # Add caption to the video and save it
            add_caption_to_video(input_file, caption, output_file)
            
            # Append the output video file name to the list
            processed_videos.append(output_file)
        except Exception as e:
            print(traceback.format_exc())

            print("Error in :", e)

    # FFmpeg command to merge all processed videos into one final video
    merge_command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "inputs.txt",  # List of input files to merge
        "-c:v", "libx264",    # Re-encode video using x264 codec
        "-c:a", "aac",        # Re-encode audio using AAC codec
        "-strict", "experimental",  # Allow experimental features if necessary
        ".\\outputs\\final_output_video.mp4"
    ]

    # Create a file with the list of input videos for merging
    with open("inputs.txt", "w") as f:
        for video in processed_videos:
            f.write(f"file '{video}'\n")

    # Run the FFmpeg command to merge videos
    try:
        subprocess.run(merge_command, check=True)
        print("Videos successfully merged into final_output_video.mp4")
    except subprocess.CalledProcessError as e:
        print(traceback.format_exc())
        print("Error occurred while merging videos:", e)

    return True