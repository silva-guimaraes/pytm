#!/usr/bin/python3

# pytm: Parse YouTube Music

from bs4 import BeautifulSoup
import yt_dlp as ydl
import requests
import sys
import re
import os

rym = ""
album_title = ""

if len(sys.argv) >= 2:
    video_url = sys.argv[1]
else: 
    print('video?')
    exit(1)
if len(sys.argv) == 3:
    rym = sys.argv[2]

class track:
    # artist = []
    title = ""
    position = 0
    start = 0
    end = 0

    def __init__(self, title, position, start, end):
        # self.artist = artist
        self.title = title
        self.position = position
        self.start = start
        self.end = end

    def __str__(self):
        return '{} - {} from {} to {} spamming {} seconds'.format(
            self.position, self.title, self.start, self.end, self.end - self.start)


track_list = []
if rym:
    # rym automaticamente bloqueia qualquer ip com o user-agent padrão do requests.get()
    headers = {'sec-ch-ua': '\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\",\
    \"Google Chrome\";v=\"101\"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '\"Linux\"',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
    (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,\
    image/avif,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br'}
    try:
        print('pedido para {}...'.format(rym))
        rym_page = requests.get(rym, headers=headers)
    except requests.exceptions.ConnectionError:
        print('falha em estabelecer nova conexão. saindo e sinalizando como erro.',
            file=sys.stderr)
        exit(1)

    rym_page = BeautifulSoup(rym_page.text, 'html.parser')
    album_title = rym_page.find_all('div', {'class': 'album_title'})[0].contents[0].strip()
    print(album_title)
    track_starts = 0
    tracks = rym_page.find(id='tracks')
    # a ultima tag é apenas o tamanho total do album. não uma faixa.
    for position, i in enumerate(tracks.contents[:-1]):
        title = i.contents[0].contents[2].contents[0].contents[0].string.strip()
        # title = i.contents[0].contents[2].contents[0].contents[0].contents[1].string[3:]
        timestamp = i.contents[0].contents[2].contents[1].string.strip() 
        seconds = int(re.search("[^:]\d*$", timestamp).group())
        minutes = 60 * int(re.search("^\d*[^:]", timestamp).group())
        duration = minutes + seconds
        new_track = track(title, position + 1, track_starts, track_starts + duration)
        print(new_track)
        track_list.append(new_track)
        track_starts += duration

options = ydl.YoutubeDL(
    {'format': 'mp4',
    'allow_multiple_audio_stream': False,
    'allow_multiple_video_stream': False
    })

chapters = []
result = {}
with options as ydl:
    result = ydl.extract_info(
        video_url,
        download=False)
    chapters = result['chapters']
    if chapters or rym:
        result = ydl.extract_info(
            video_url,
            download=True)
    elif not rym:
        print('vídeo não possui capítulos.')
        exit(1)

# / (barra) é o denominador de diretórios no linux e mac e \ (contra barra) no windows
# nenhuma faixa pode ter nenhum desses dois caracteres então nós trocamos por algum outro
# caractere antes de separar a faixa
def replace_slash(s):
    s = s.replace('/', '|')
    s = s.replace('\\', '|')
    return s
# todo: salva o nome original da faixa nos metadados

def splice_video(basename, start, end):
    video_path = result['requested_downloads'][0]['filepath']
    filename = replace_slash(basename) + ".mp3"
    if album_title:
        yt_video_title = replace_slash(album_title)
    else:
        yt_video_title = replace_slash(result['title'])
    if not os.path.exists(yt_video_title):
        os.makedirs(yt_video_title)
    output_path = os.path.join(yt_video_title, filename)
    print('[pytm] enconding: {}...'.format(basename))
    command = 'ffmpeg -hide_banner -loglevel error -ss "{}" -to "{}" -i "{}" -vn "{}"'
    os.system(command.format(start, end, video_path, output_path))


def split_chapters(chapters):
    for i in chapters:
        splice_video(i['title'], i['start_time'], i['end_time'])


def split_duration(track_list):
    for i in track_list:
        splice_video('{:02d}. {}'.format(i.position, i.title),
                     i.start, i.end) 
        

if rym:
    split_duration(track_list)
else:
    split_chapters(chapters)


# os.remove(filepath)
