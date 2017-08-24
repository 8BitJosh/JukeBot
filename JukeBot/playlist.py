import os, shutil
import youtube_dl
import traceback
import datetime
import time

from random import shuffle
from utils import do_format, PlaylistEntry, delete_file

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


class Playlist:
    def __init__(self, _config):
        self.config = _config

        self.songqueue = []
        self.currently_play = ''
        self.playlist_updated = True

        self.savedir = "cache"
        if os.path.exists(self.savedir):
            shutil.rmtree(self.savedir)
        os.makedirs(self.savedir)

    def shuff(self):
        shuffle(self.songqueue)
        self.playlist_updated = True
        print("Playlist Shuffled", flush=True)

    def empty(self):
        if self.songqueue:
            return False
        else:
            self.currently_play = ''
            self.playlist_updated = True
            return True

    def get_next(self):
        while not self.songqueue[0].downloaded:
            time.sleep(0.1)
        self.currently_play = "[" + str(datetime.timedelta(seconds=self.songqueue[0].duration)) + "] " + self.songqueue[0].title
        song = self.songqueue[0]
        print("Removed from to play queue - " + self.songqueue[0].title, flush=True)
        del self.songqueue[0]
        self.playlist_updated = True
        return song

    def getPlaylist(self):
        endmsg = {}
        totalDur = 0

        if self.currently_play == '':
            endmsg['-'] = ''
        else:
            count = 0
            endmsg[str(count)] = self.currently_play
            for things in self.songqueue:
                count += 1
                endmsg[str(count)] =  "[" + str(datetime.timedelta(seconds=things.duration)) + ']  ' + things.title
                totalDur += things.duration
            endmsg['dur'] = str(datetime.timedelta(seconds=totalDur))

        return endmsg

    def updated(self):
        if self.playlist_updated:
            self.playlist_updated = False
            return True
        else:
            return False

    def remove(self, _index, _title):
        index = _index - 1
        start = _title.find(']') + 2
        title = _title[start:]

        try:
            playlistTitle = self.songqueue[index].title   
            del_path = self.songqueue[index].dir
        except IndexError:
            print('More than one user removed a song at the same time', flush=True)
            return
        
        if title.strip() == playlistTitle.strip():    
            del self.songqueue[index]
            self.playlist_updated = True
            if del_path != '':
                delete_file(del_path)
        else:
            print('More than one user removed a song at the same time', flush=True)
            return

    def clearall(self):
        while len(self.songqueue):
            if self.songqueue[0].dir != '':
                delete_file(self.songqueue[0].dir)
            del self.songqueue[0]

        self.songqueue.clear()
        self.playlist_updated = True

    # called when user enters song to be processed
    def process(self, _title):
        print('process called', flush=True)
        song_url = _title.strip()
        ydl = youtube_dl.YoutubeDL(options)

####get info for song
        try:
            info = ydl.extract_info(song_url, download = False, process = False)
        except Exception:
            print('info extraction error', flush=True)
            pass

####if song is search term

        if info.get('url', '').startswith('ytsearch'):
            info = ydl.extract_info(song_url, download = False, process = True)
            if not info:
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
                print('oh no url YT error again', flush=True)

####if song is playlist
        elif 'entries' in info:
            try:
                info = ydl.extract_info(song_url, download=False, process=False)
            except Exception as e:
                print('Could not extract information from {}\n\n{}'.format(playlist_url, e), flush=True)
                return

            if not info:
                print('Could not extract information from %s' % playlist_url, flush=True)
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
                            playlist_info['title'],
                            playlist_info['duration']
                        )
                        print('added from playlist - ' + playlist_info['title'], flush=True)
                        self.songqueue.append(entry)
                        self.playlist_updated = True
                    except Exception as e:
                        baditems += 1
                        print('There was an error adding the song from playlist', flush=True)
                        print(e)
                else:
                    baditems += 1
            if baditems:
                print('Skipped %s bad entries' % baditems, flush=True)

            print('Added {}/{} songs from playlist'.format(items - baditems, items), flush=True)

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
                print('Error with other option', flush=True)

        print('user input processed - ' + _title, flush=True)
        self.playlist_updated = True

    #download next non downloaded song
    def download_next(self):
        for things in self.songqueue:
            if things.downloaded == False:
                if things.downloading == True:
                    break
                things.downloading = True
                things.dir = self.download_song(things)
                things.downloaded = True
                break

    #download song from url or search term and return the save path of the file
    def download_song(self, to_down):
        song_url = to_down.url.strip()
        ydl = youtube_dl.YoutubeDL(options)
        print('Starting to download - ' + to_down.title, flush=True)

        try:
            title = do_format(to_down.title)
            title = title + '-' + str(int(time.time()))
            savepath = os.path.join(self.savedir, "%s" % (title))
        except Exception as e:
            print("Can't access song! %s\n" % traceback.format_exc(), flush=True)
            return 'bad_path'

        try:
            os.stat(savepath)
            return savepath
        except OSError:
            try:
                result = ydl.extract_info(song_url, download=True)
                os.rename(result['id'], savepath)
                print('Downloaded - ' + to_down.title, flush=True)
                return savepath
            except Exception as e:
                print ("Can't download audio! %s\n" % traceback.format_exc(), flush=True)
                return 'bad_path'
