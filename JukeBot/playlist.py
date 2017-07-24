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
    'noplaylist' : False,   ################
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
        
        self.savedir = "cache"
        if os.path.exists(self.savedir):
            shutil.rmtree(self.savedir)
        os.makedirs(self.savedir)
        
    def shuff(self):
        shuffle(self.songlist)
        print("Playlist Shuffled")
    
    def empty(self):
        if self.songqueue:
            return False
        else:
            self.currently_play = ''
            return True
    
    def get_next(self):
        self.currently_play = "Now : [" + str(datetime.timedelta(seconds=self.songqueue[0].duration)) + "] " + self.songqueue[0].title + " \n"
        path = self.songqueue[0].dir
        print("Removed from to play queue - " + self.songqueue[0].title)
        del self.songqueue[0]
        return path
        
    def add(self, title):
        self.songlist.append(title)

    def process(self):
        for things in self.songlist:
            print("process called")
            song_url = things.strip()
            ydl = youtube_dl.YoutubeDL(options)
            
####get info for song
            try:
                info = ydl.extract_info(song_url, download = False, process = False)
            except Exception:
                print("info extraction error")
                pass
                
####if song is search term
            
            if info.get('url', '').startswith('ytsearch'):
                info = ydl.extract_info(song_url, download = False, process = True)
                if not info:
                    self.songlist.remove(things)
                    return
                if not all(info.get('entries', [])):
                    return
                
                song_url = info['entries'][0]['webpage_url']
                   
                info = ydl.extract_info(song_url, download = False, process = False)

                try:
                    entry = PlaylistEntry(
                        song_url,
                        info['title'],
                        info['duration']
                    )
                    self.songqueue.append(entry)
                except:
                    print("oh no url YT error again")

####if song is playlist
            elif 'entries' in info:
                try:
                    info = ydl.extract_info(song_url, download=False, process=False)
                except Exception as e:
                    print('Could not extract information from {}\n\n{}'.format(playlist_url, e))
                    return

                if not info:
                    print('Could not extract information from %s' % playlist_url)
                    return
                    
                items = 0
                baditems = 0
                for entry_data in info['entries']:
                    items += 1
                    if entry_data:
                        baseurl = info['webpage_url'].split('playlist?list=')[0]
                        song_url = baseurl + 'watch?v=%s' % entry_data['id']
                        try:
                            playlist_info = ydl.extract_info(song_url, download=False, process=True)
                            entry = PlaylistEntry(
                                song_url,
                                #playlist_info['url'],
                                playlist_info['title'],
                                playlist_info['duration']
                            )
                            print(playlist_info['title'] + " added from playlist")
                            self.songqueue.append(entry)
                        except Exception as e:
                            baditems += 1
                            print("There was an error adding the song from playlist")
                            print(e)
                    else:
                        baditems += 1

                if baditems:
                    print("Skipped %s bad entries" % baditems)
        
                print('Added {}/{} songs from playlist'.format(items - baditems, items))

####else if song is a url or other thing
            else:
                info = ydl.extract_info(song_url, download = False, process = True)
                try:
                    entry = PlaylistEntry(
                        song_url,
                        info['title'],
                        info['duration']
                    )
                    self.songqueue.append(entry)
                except:
                    print("Error with other option")

            print("user input processed - " + things)
            while things in self.songlist: self.songlist.remove(things)

    #download next non downloaded song
    def download_next(self):
        for things in self.songqueue:
            if things.downloaded == False:
                things.dir = self.download_song(things)
                things.downloaded = True
                break
           

    #itterate through playlist get the title from youtube url search and print to screen
    def getPlaylist(self):
        endmsg = self.currently_play
        count = 0
        for things in self.songqueue:
            count += 1
            endmsg = endmsg + str(count) + ": [" + str(datetime.timedelta(seconds=things.duration)) + ']  ' + things.title + " \n"
        return endmsg
    
    
    #download song from url or search term and return the save path of the file
    def download_song(self, to_down):
        song_url = to_down.url.strip()
        ydl = youtube_dl.YoutubeDL(options)
        
        try:
            title = do_format(to_down.title)
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
                print("Downloaded - " + savepath)
                return savepath
            except Exception as e:
                print ("Can't download audio! %s\n" % traceback.format_exc())
                return 'bad_path'