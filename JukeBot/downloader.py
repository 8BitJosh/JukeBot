import asyncio
import youtube_dl
import functools

from concurrent.futures import ThreadPoolExecutor

options = {
    'format': 'bestaudio/best',
    'extractaudio' : True,
    'audioformat' : "mp3",
    'outtmpl': '%(id)s',
    'noplaylist' : False,   
    'nocheckcertificate' : True,
    'ignoreerrors' : True,
    'quiet' : True,
    'no_warnings' : True,
    'default_search': 'ytsearch',
    }

class Downloader:
    def __init__(self, save_dir):
        self.threadPool = ThreadPoolExecutor(max_workers=2)
        options['progress_hooks'] = [self.hook]

        self.ydl = youtube_dl.YoutubeDL(options)
        self.saveDir = save_dir


    async def extract_info(self, loop, url, download, process):
        return await loop.run_in_executor(self.threadPool, functools.partial(self.ydl.extract_info, url=url, download=download, process=process))


    def hook(self, data):
        if data['status'] == 'finished':
            print('Downloaded {} in {}'.format(data['_total_bytes_str'], data['_elapsed_str'])) 
            