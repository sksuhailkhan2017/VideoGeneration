import subprocess
import json

# JSON data with video clips and captions
data = [
    {
        "clip": [
            "clips\\166273_clips\\166273_clip_4_9.mp4"
        ],
        "caption": "Boost productivity with EmpMonitor!"
    },
    {
        "clip": [
            "clips\\202135_clips\\202135_clip_4_9.mp4"
        ],
        "caption": "Time matters. Track employee activity."
    },
    {
        "clip": [
            "clips\\112722_clips\\112722_clip_13_18.mp4"
        ],
        "caption": "Sale now live! Get EmpMonitor today."
    },
    {
        "clip": [
            "clips\\121996_clips\\121996_clip_10_15.mp4"
        ],
        "caption": "Improve efficiency.  EmpMonitor helps."
    },
    {
        "clip": [
            "clips\\2176_clips\\2176_clip_5_10.mp4"
        ],
        "caption": "See real-time data. Make informed decisions."
    },
    {
        "clip": [
            "clips\\190332_clips\\190332_clip_2_7.mp4"
        ],
        "caption": "Time is money. Optimize with EmpMonitor."
    },
    {
        "clip": [
            "clips\\2340_clips\\2340_clip_30_35.mp4"
        ],
        "caption": "Elevate your team's performance."
    }
]

# Function to apply caption to a video
def add_caption_to_video(input_file, caption, output_file):
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
               f"text='{caption}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100",
        "-codec:a", "copy",
        output_file
    ]
    
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing {input_file}: {e}")

# List to hold the names of processed video files
processed_videos = []

# Process each clip and add its caption
for idx, item in enumerate(data):
    input_file = item["clip"][0]
    caption = item["caption"]
    output_file = f".\\outputs\\output_video_{idx+1}.mp4"
    
    # Add caption to the video and save it
    add_caption_to_video(input_file, caption, output_file)
    
    # Append the output video file name to the list
    processed_videos.append(output_file)

# FFmpeg command to merge all processed videos into one final video
merge_command = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", "inputs.txt",  # List of input files to merge
    "-c", "copy",
    "final_output_video.mp4"
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
    print("Error occurred while merging videos:", e)
