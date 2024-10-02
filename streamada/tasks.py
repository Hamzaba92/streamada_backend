import subprocess



def convert_video(source, resolution, label):
    """
    Converts the video to the specified resolution and saves it with the specified label like => 480p, 720p and 1080p.
    """
    target = source.replace('.mp4', f'_{label}.mp4')
    cmd = 'ffmpeg -i "{}" -s {} -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, resolution, target)
    subprocess.run(cmd, shell=True)
    return target

