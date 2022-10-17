
# pytm: Parse Youtube Music

import yt_dlp as ydl
import os
import sys

if len(sys.argv) >= 2:
    video = sys.argv[1]
else: 
    print('video?')
    exit(1)

options = ydl.YoutubeDL(
    {'format': 'mp4',
     'allow_multiple_audio_stream': False,
     'allow_multiple_video_stream': False
     })

with options as ydl:
    result = ydl.extract_info(
        video,
        download=True)

chapters = result['chapters']

if not chapters:
    exit(0)

filepath = result['requested_downloads'][0]['filepath']
base_dir = os.path.dirname(filepath)
basename = result['title']

if not os.path.exists(basename):
    os.makedirs(basename)

result_dir = os.path.join(base_dir, basename)

for i in chapters:
    title = i['title']
    output_path = os.path.join(result_dir, title + ".ogg")
    command = 'ffmpeg -hide_banner -loglevel error -ss "{}" -to "{}" -i "{}" -vn -c copy "{}"'
    command = command.format(i['start_time'],
                             i['end_time'],
                             filepath,
                             output_path)
    print(title + '...')
    os.system(command)

# os.remove(filepath)
