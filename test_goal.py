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
        ts_files = [filename for filename in os.listdir(folder_path) if
                    filename.endswith(".ts") and is_valid_video(os.path.join(folder_path, filename))]

        # Find the latest numeric part without sorting
        # Extract all numeric parts
        numeric_parts = sorted([int(''.join(filter(str.isdigit, ts_file))) for ts_file in ts_files], reverse=True)

        # Find the latest and second latest numeric parts
        file_1, file_2 = numeric_parts[1], numeric_parts[2]

        file_2_filename = f"{title}_{file_2:03d}.ts"  # Assuming you want to format the filename as "_004"
        file_1_filename = f"{title}_{file_1:03d}.ts"
        ts_file_paths = [os.path.join(folder_path, file_1_filename), os.path.join(folder_path, file_2_filename)]

        with open(os.path.join(folder_path, 'file_list.txt'), 'w') as file_list:
            for ts_file in ts_file_paths:
                file_list.write(f"file '{ts_file}'\n")

        ffmpeg_command = (
            f'ffmpeg -f concat -safe 0 -i "{os.path.join(folder_path, "file_list.txt")}" '
            f'-c copy "{os.path.join(folder_path, filename)}"'
        )

        subprocess.run(ffmpeg_command, shell=True)

        os.remove(os.path.join(folder_path, 'file_list.txt'))

        base_filename, extension = os.path.splitext(filename)
        public_id = base_filename

        # secure_url = self.upload_to_cloudinary(os.path.join(folder_path, latest_filename.replace(".ts", ".mp4")),
        #                                        public_id)
        print("secure_url", public_id)
        # return secure_url
    else:
        print(f"Folder not found: {folder_path}")

save_goal("Lamia vs Olympiacos", "Lamia vs Olympiacos_5-0.mp4")
