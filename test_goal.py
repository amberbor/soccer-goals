import os
import subprocess
from moviepy.editor import VideoFileClip

def is_valid_video(file_path):
    try:
        VideoFileClip(file_path)
        return True
    except Exception as e:
        print(f"Invalid video file: {file_path}. Error: {e}")
        return False

def save_goal(title, filename):
    print("Goaaaaaaaaaal")

    folder_path = os.path.join(os.getcwd(), title)

    if os.path.exists(folder_path):
        ts_files = [filename for filename in os.listdir(folder_path) if filename.endswith(".ts") and is_valid_video(os.path.join(folder_path, filename))]

        ts_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)) if os.path.isfile(os.path.join(folder_path, x)) else 0, reverse=True)

        latest_ts_files = ts_files[:2][::-1]


        if len(latest_ts_files) == 2:
            ts_file_paths = [os.path.join(folder_path, ts_file) for ts_file in latest_ts_files]

            with open(os.path.join(folder_path, 'file_list.txt'), 'w') as file_list:
                for ts_file in ts_file_paths:
                    file_list.write(f"file '{ts_file}'\n")

            ffmpeg_command = (
                f'ffmpeg -f concat -safe 0 -i "{os.path.join(folder_path, "file_list.txt")}" '
                f'-c copy "{os.path.join(folder_path, filename)}"'
            )

            subprocess.run(ffmpeg_command, shell=True)

            os.remove(os.path.join(folder_path, 'file_list.txt'))

            print(f"Successfully created {os.path.join(folder_path, 'final.mp4')}")
        else:
            print("Not enough valid '.ts' files to create an MP4")
    else:
        print(f"Folder not found: {folder_path}")

save_goal("Ibri vs Bahla")
