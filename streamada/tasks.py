import subprocess
import os


def convert_video(source, resolution, label):
    """
    Converts the video to the specified resolution and saves it with the specified label like => 480p, 720p and 1080p.
    """
    target = source.replace('.mp4', f'_{label}.mp4')
    cmd = 'ffmpeg -i "{}" -s {} -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, resolution, target)
    subprocess.run(cmd, shell=True)
    return target



def delete_original_file(file_path):
    print(f"Attempting to delete file: {file_path}")
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"Uploadfile deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    else:
        print(f"Uploadfile not found: {file_path}")