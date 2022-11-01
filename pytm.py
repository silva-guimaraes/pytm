#!/usr/bin/python3

# pytm: Parse YouTube Music

from bs4 import BeautifulSoup
from typing import List, Tuple, Any, Dict, Union, SupportsIndex
import shutil
import yt_dlp
import requests
import sys
import re
import os

# todo: classes para cada site diferente

# rym automaticamente bloqueia qualquer ip com o user-agent padrão do requests.get()
# favor não fazer nenhum request sem antes especificar esse header
headers = {'sec-ch-ua': '\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\",\
\"Google Chrome\";v=\"101\"',
        'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '\"Linux\"',
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

class track:
    # artist = []
    title = ""
    position = 0
    start = 0
    end = 0

    def __init__(self, title: str, position: int, start: int, end: int):
        # self.artist = artist
        self.title = title
        self.position = position
        self.start = start
        self.end = end

    def __str__(self):
        return '{} - {} from {} to {} spamming {} seconds'.format(
            self.position, self.title, self.start, self.end, self.end - self.start)


def extract_rym(rym_url: str) -> Tuple[List[track], str, object]:
    rym_page: object
    try:
        print('pedido para {}...'.format(rym_url))
        rym_page = requests.get(rym_url, headers=headers)
    except requests.exceptions.ConnectionError:
        print('falha em estabelecer nova conexão. saindo e sinalizando como erro.',
            file=sys.stderr)
        exit(1)

    track_list: List[track] = []
    rym_page = BeautifulSoup(rym_page.text, 'html.parser')
    album_title: str = rym_page.select('#column_container_right > div.section_main_info\
.section_outer > div > div.album_title')[0].contents[0].string.strip()

    # album_title = rym_page.find_all('div', {'class': 'album_title'})[0].contents[0].strip()
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

    return track_list, album_title, rym_page

# / (barra) é o denominador de diretórios no linux e mac e \ (contra barra) no windows
# nenhuma faixa pode ter nenhum desses dois caracteres então nós trocamos por algum outro
# caractere antes de separar a faixa
def replace_slash(s: str) -> str:
    s = s.replace('/', '|')
    s = s.replace('\\', '|')
    return s
# todo: salva o nome original da faixa nos metadados

def create_album_dir(metadata: dict, album_title: str) -> str:
    yt_video_title = ""

    if album_title:
        yt_video_title = replace_slash(album_title)
    else:
        yt_video_title = replace_slash(metadata['title'])

    if not os.path.exists(yt_video_title):
        os.makedirs(yt_video_title)

    return yt_video_title

    
def splice_video(metadata: dict, yt_video_title: str, basename: str,
                 start, end):
    video_path = metadata['requested_downloads'][0]['filepath']
    filename = replace_slash(basename) + ".mp3"
    output_path = os.path.join(yt_video_title, filename)
    print('[pytm] enconding: {}...'.format(basename))
    command = 'ffmpeg -hide_banner -loglevel error -ss "{}" -to "{}" -i "{}" -vn "{}"'
    os.system(command.format(start, end, video_path, output_path))

def split_chapters(metadata: dict, yt_video_title: str, chapters: List[Any]):
    for i in chapters:
        splice_video(metadata, yt_video_title, i['title'], i['start_time'], i['end_time'])


def split_duration(metadata: dict, yt_video_title: str, track_list: List[track]):
    for i in track_list:
        splice_video(metadata, yt_video_title, '{:02d}. {}'.format(i.position, i.title),
                     i.start, i.end) 
        
def download_cover(album_dir: str, url: str):
    local_filename = os.path.join(album_dir,'cover.png')
    with requests.get(url, stream=True, headers=headers) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def main():
    track_list: List[track] = []
    album_title: str = ""
    video_url: str = ""
    rym_url: str = ""
    
    if len(sys.argv) >= 2:
        video_url = sys.argv[1]
    else: 
        print('video?')
        exit(1)
    if len(sys.argv) == 3:
        rym_url = sys.argv[2]
        track_list, album_title, rym_page = extract_rym(rym_url)

    options = yt_dlp.YoutubeDL(
        {'format': 'mp4',
        'allow_multiple_audio_stream': False,
        'allow_multiple_video_stream': False
        })

    chapters = []
    metadata = {}
    with options as ydl:
        metadata = ydl.extract_info(video_url, download=False)
        chapters = metadata['chapters']
        if chapters or track_list:
            metadata = ydl.extract_info(video_url, download=True)
        elif not rym:
            print('vídeo não possui capítulos.')
            exit(1)

    yt_video_title = create_album_dir(metadata, album_title)
    if track_list:
        split_duration(metadata, yt_video_title, track_list)
        album_link = rym_page.select('#column_container_left > div.page_release_art_frame\
 > div > a > div > img')[0]['src']
        download_cover(yt_video_title, 'https:' + album_link)
    else:
        split_chapters(metadata, chapters)

    # os.remove(filepath)

if __name__ == "__main__":
    main()
