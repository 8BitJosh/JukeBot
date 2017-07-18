import os, shutil
import subprocess
import youtube_dl
import traceback
import datetime
import time
from random import shuffle
from utils import do_format
from utils import PlaylistEntry

options = {
    'format': 'bestaudio/best',
    'extractaudio' : True,
    'audioformat' : "mp3",
    'outtmpl': '%(id)s',
    'noplaylist' : True,
    'nocheckcertificate' : True,
    'ignoreerrors' : True,
    'quiet' : True,
    'no_warnings' : True,
    'default_search': 'ytsearch',
    }

class Playlist:
    

    def __init__(self):
        self.songlist = []
        self.songqueue = []
        self.currently_play = ''
        
        self.savedir = "playlist"
        if os.path.exists(self.savedir):
            shutil.rmtree(self.savedir)
        os.makedirs(self.savedir)
        
    def shuff(self):
        shuffle(self.songlist)
    
    def empty(self):
        if self.songqueue:
            return False
        else:
            return True
    
    def get_next(self):
        return self.songqueue[0].url
        
    def remove(self, thing):
        self.currently_play = "Now : [" + str(datetime.timedelta(seconds=self.songqueue[0].duration)) + "] " + self.songqueue[0].title + " \n"
        print("remove")
        #while thing in self.songqueue: self.songqueue.remove(thing)
        del self.songqueue[0]
    
    def add(self, title):
        self.songlist.append(title)

    def process(self):
        for things in self.songlist:
            print("processed")
            song_url = things.strip()
            ydl = youtube_dl.YoutubeDL(options)

            try:
                info = ydl.extract_info(song_url, download = False, process = False)
            except Exception:
                print("error")
                pass
            
            if info.get('url', '').startswith('ytsearch'):
                info = ydl.extract_info(song_url, download = False, process = True)
            
                if not all(info.get('entries', [])):
                    return
                
                song_url = info['entries'][0]['webpage_url']
                info = ydl.extract_info(song_url, download = False, process = False)

            try:
                entry = PlaylistEntry(
                    things,
                    info['title'],
                    info['duration']
                )
            except:
                print("oh no url YT error again")
                
            self.songqueue.append(entry)
            while things in self.songlist: self.songlist.remove(things)

    #itterate through playlist get the title from youtube url search and print to screen
    def getPlaylist(self):
        endmsg = self.currently_play
        count = 0
        for things in self.songqueue:
            count += 1
            endmsg = endmsg + str(count) + ": [" + str(datetime.timedelta(seconds=things.duration)) + ']  ' + things.title + " \n"
        return endmsg
    
    
    #download song from url or search term and return the save path of the file
    def download_song(self, unfixedsongURL):
        print("download")
        song_url = unfixedsongURL.strip()
        ydl = youtube_dl.YoutubeDL(options)
        try:
            info = ydl.extract_info(song_url, download = False, process = False)
        except Exception:
            print("error")
            pass
        if not info:
            print("Ths video cannot be played")
            return
            
        if info.get('url', '').startswith('ytsearch'):
            info = ydl.extract_info(song_url, download = False, process = True)
            
            if not all(info.get('entries', [])):
                return
                
            song_url = info['entries'][0]['webpage_url']
            info = ydl.extract_info(song_url, download = False, process = False)

        try:
            title = info['title']
            title = do_format(title)
            savepath = os.path.join(self.savedir, "%s.mp3" % (title))
        except Exception as e:
            print("Can't access song! %s\n" % traceback.format_exc())
            return 'bad_path'

        try:
            os.stat(savepath)
            return savepath
        except OSError:
            try:
                result = ydl.extract_info(song_url, download=True)
                os.rename(result['id'], savepath)
                print("Downloaded")
                return savepath
            except Exception as e:
                print ("Can't download audio! %s\n" % traceback.format_exc())
                return 'bad_path'