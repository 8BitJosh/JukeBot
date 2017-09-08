import os, shutil
import youtube_dl
import traceback
import datetime
import time

import asyncio

from random import shuffle
from utils import do_format, PlaylistEntry, delete_file
from downloader import Downloader

class ExtractionError(Exception):
    def __init__(self, message):
        self._message = message

    @property
    def message(self):
        return self._message

class Playlist:
    def __init__(self, _config, _socketio, loop):
        self.config = _config
        self.socketio = _socketio
        self.loop = loop

        self.songqueue = []
        self.currently_play = ''

        self.savedir = "cache"
        if os.path.exists(self.savedir):
            shutil.rmtree(self.savedir)
        os.makedirs(self.savedir)

        self.downloader = Downloader(self.savedir)

    async def shuff(self):
        shuffle(self.songqueue)
        await self.sendPlaylist()

    async def empty(self):
        if self.songqueue:
            return False
        elif self.currently_play == '':
            return True
        else:
            self.currently_play = ''
            await self.sendPlaylist()
            return True

    async def get_next(self):
        if not self.songqueue[0].downloaded:
            asyncio.sleep(0.5)
            return  PlaylistEntry('', 'title', 0)

        self.currently_play = "[" + str(datetime.timedelta(seconds=int(self.songqueue[0].duration))) + "] " + self.songqueue[0].title
        song = self.songqueue[0]
        print("Removed from to play queue - " + self.songqueue[0].title, flush=True)
        del self.songqueue[0]
        await self.sendPlaylist()
        return song

    async def sendPlaylist(self):
        endmsg = {}
        totalDur = 0

        if self.currently_play == '':
            endmsg['-'] = ''
        else:
            count = 0
            endmsg[str(count)] = self.currently_play
            for things in self.songqueue:
                count += 1
                endmsg[str(count)] =  "[" + str(datetime.timedelta(seconds=int(things.duration))) + ']  ' + things.title
                totalDur += things.duration
            endmsg['dur'] = str(datetime.timedelta(seconds=int(totalDur)))

        await self.socketio.emit('sent_playlist', endmsg, namespace='/main')

    async def remove(self, _index, _title):
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
            await self.sendPlaylist()
            if del_path != '':
                delete_file(del_path)
        else:
            print('More than one user removed a song at the same time', flush=True)
            return

    async def clearall(self):
        while len(self.songqueue):
            if self.songqueue[0].dir != '':
                delete_file(self.songqueue[0].dir)
            del self.songqueue[0]

        self.songqueue.clear()
        await self.sendPlaylist()

    async def addPlaylist(self, songs, requester):
        for song in songs
            if 'data' not in song:
                try:
                    info = await self.downloader.extract_info(self.loop, songs[song]['url'], download = False, process = False)
                    entry = PlaylistEntry(
                        songs[song]['url'],
                        info['title'],
                        info['duration'],
                        requester
                    )
                    self.songqueue.append(entry)
                except:
                    print('Server Playlist has a bad URL', flush=True)

    # called when user enters song to be processed
    async def process(self, _title, _requester):
        print('process called', flush=True)
        song_url = _title.strip()

####get info for song
        try:
            info = await self.downloader.extract_info(self.loop, song_url, download = False, process = False)
        except Exception:
            print('info extraction error', flush=True)
            pass

####if song is search term

        if info.get('url', '').startswith('ytsearch'):
            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=True)
            if not info:
                return
            if not all(info.get('entries', [])):
                return

            song_url = info['entries'][0]['webpage_url']

            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=False)

            try:
                entry = PlaylistEntry(
                    song_url,
                    info['title'],
                    info['duration'],
                    _requester
                )
                self.songqueue.append(entry)
            except:
                print('oh no url YT error again', flush=True)

####if song is playlist
        elif 'entries' in info:
            try:
                info = await self.downloader.extract_info(self.loop, song_url, download=False, process=False)
            except Exception as e:
                print('Could not extract information from {}\n\n{}'.format(playlist_url, e), flush=True)
                return

            if not info:
                print('Could not extract information from %s' % playlist_url, flush=True)
                return

            items = 0
            baditems = 0
            playlist_url = song_url
    # youtube playlist
            if info['extractor'].lower() == 'youtube:playlist':
                try:
                    for entry_data in info['entries']:
                        items += 1
                        if entry_data:
                            baseurl = info['webpage_url'].split('playlist?list=')[0]
                            song_url = baseurl + 'watch?v=%s' % entry_data['id']
                            try:
                                try:
                                    playlist_info = await self.downloader.extract_info(self.loop, song_url, download=False, process=False)
                                except Exception as e:
                                    raise ExtractionError('Could not extract information from {}\n\n{}'.format(song_url, e))

                                entry = PlaylistEntry(
                                    song_url,
                                    playlist_info.get('title', 'Untitled'),
                                    playlist_info.get('duration', 0) or 0,
                                    _requester
                                )
                                print('added from playlist - ' + playlist_info['title'], flush=True)
                                self.songqueue.append(entry)
                                await self.sendPlaylist()
                            except ExtractionError:
                                baditems += 1
                            except Exception as e:
                                baditems += 1
                                print('There was an error adding the song from playlist %s' %  entry_data['id'], flush=True)
                                print(e)
                        else:
                            baditems += 1

                except Exception:
                    print('Error handling playlist %s queuing.' % playlist_url, flush=True)
    # soundcloud and bandcamp
            elif info['extractor'].lower() in ['soundcloud:set', 'soundcloud:user', 'bandcamp:album']:
                try:
                    for entry_data in info['entries']:
                        items += 1
                        if entry_data:
                            song_url = entry_data['url']
                            try:
                                try:
                                    playlist_info = await self.downloader.extract_info(self.loop, song_url, download=False, process=False)
                                except Exception as e:
                                    raise ExtractionError('Could not extract information from {}\n\n{}'.format(song_url, e))

                                entry = PlaylistEntry(
                                    song_url,
                                    playlist_info.get('title', 'Untitled'),
                                    playlist_info.get('duration', 0) or 0,
                                    _requester
                                )
                                print('added from playlist - ' + playlist_info['title'], flush=True)
                                self.songqueue.append(entry)
                                await self.sendPlaylist()
                            except ExtractionError:
                                baditems += 1
                            except Exception as e:
                                baditems += 1
                                print('There was an error adding the song from playlist %s' %  entry_data['id'], flush=True)
                                print(e)
                        else:
                            baditems += 1

                except Exception:
                    print('Error handling playlist %s queuing.' % playlist_url, flush=True)

            if baditems:
                print("Skipped %s bad entries" % baditems, flush=True)

            print('Added {}/{} songs from playlist'.format(items - baditems, items), flush=True)

####else if song is a url or other thing
        else:
            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=True)
            try:
                entry = PlaylistEntry(
                    song_url,
                    info['title'],
                    info['duration'],
                    _requester
                )
                self.songqueue.append(entry)
            except:
                print('Error with other option', flush=True)

        print('user input processed - ' + _title, flush=True)
        await self.sendPlaylist()

    #download next non downloaded song
    async def download_next(self):
        for things in self.songqueue:
            if things.downloaded == False:
                if things.downloading == True:
                    break
                things.downloading = True
                things.dir = await self.download_song(things)
                things.downloaded = True
                break

    #download song from url or search term and return the save path of the file
    async def download_song(self, to_down):
        song_url = to_down.url.strip()
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
                result = await self.downloader.extract_info(self.loop, song_url, download=True, process=True)
                os.rename(result['id'], savepath)
                print('Downloaded - ' + to_down.title, flush=True)
                return savepath
            except Exception as e:
                print ("Can't download audio! %s\n" % traceback.format_exc(), flush=True)
                return 'bad_path'
