import subprocess

# "ffmpeg -t 30 -i $(youtube-dl -g -f best 'https://tens.livetwoassia.online/hls/41.m3u8?md5=gUI_j4EvKElFfUchlNeYOQ&expires=1698757799') -y output.mp4"

# Define the filename and URL as variables
filename = "output.mp4"
url = "https://tens.livetwoassia.online/hls/41.m3u8?md5=gUI_j4EvKElFfUchlNeYOQ&expires=1698757799"

# Construct the command with the variables
command = [
    "ffmpeg",
    "-t", "30",
    "-i",
    subprocess.check_output(["youtube-dl", "-g", "-f", "best", url]).decode().strip(),
    "-y", filename
]

# Execute the command
subprocess.run(command)


