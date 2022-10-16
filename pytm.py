
import yt_dlp as ydl
import requests
import os
import sys

if len(sys.argv) == 2:
    video = sys.argv[1]
else: 
    print('video?')
    exit(1)

options = ydl.YoutubeDL(
    {'format': 'mp4',
     # 'outtmpl': '%(id)s.%(ext)s',
     'allow_multiple_audio_stream': False,
     'allow_multiple_video_stream': False
     })

with options as ydl:
    result = ydl.extract_info(
        video,
        download=True)

filepath = result['requested_downloads'][0]['filepath']
chapters = result['chapters']
base_dir = os.path.dirname(filepath)

for i in chapters:
    output_path = os.path.join(base_dir, i['title'] + ".mp4")
    command = 'ffmpeg -hide_banner -loglevel error -ss "{}" -to "{}" -i "{}" -c copy "{}"'
    command = command.format(i['start_time'],
                             i['end_time'],
                             filepath,
                             output_path)
    os.system(command)

    
    
