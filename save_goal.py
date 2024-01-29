import os
import subprocess


def save_goal(title, filename, num_to_keep=2):
    print("Goaaaaaaaaaal", title)
    full_filename = f"{filename}.mp4"

    if os.path.exists(os.path.join(os.getcwd(), title)):

        folder_path = os.path.join(os.getcwd(), title)

        if os.path.exists(os.path.join(folder_path, f'{title}.ffcat')):

            input_ffcat = os.path.join(folder_path, f'{title}.ffcat')
            output_ffcat = os.path.join(folder_path, f'{filename}.ffcat')

            command = f'tail -n {num_to_keep} "{input_ffcat}" > "{output_ffcat}"'


            try:
                subprocess.run(command, shell=True)

                ffmpeg_command = (
                    f'ffmpeg -f concat -safe 0 -i "{os.path.join(folder_path, output_ffcat)}" '
                    f'-c copy -async 1 "{os.path.join(folder_path, full_filename)}"'
                )

                subprocess.run(ffmpeg_command, shell=True)
            except Exception as e:
                print("An error occurred:", str(e))


save_goal("Galatasaray vs Gaziantep FK", "Galatasaray vs Gaziantep FK 1-0")