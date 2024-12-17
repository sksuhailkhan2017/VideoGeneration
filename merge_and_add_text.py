import subprocess

# Input and output file paths
input_file = r"clips\166273_clips\166273_clip_4_9.mp4"
output_file = "output_video.mp4"

# FFmpeg command to add text overlay with increased font size
ffmpeg_command = [
    "ffmpeg",
    "-i", input_file,
    "-vf", "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
           "text='Boost productivity with EmpMonitor!':"
           "fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100",
    "-codec:a", "copy",
    output_file
]

# Run the FFmpeg command
try:
    subprocess.run(ffmpeg_command, check=True)
    print("Video processing complete. Output saved as:", output_file)
except subprocess.CalledProcessError as e:
    print("Error occurred while processing video:", e)
