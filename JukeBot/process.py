import socketio
import asyncio
import traceback
import datetime
import time
import os

from downloader import Downloader
from utils import do_format, PlaylistEntry


class ExtractionError(Exception):
    def __init__(self, message):
        self._message = message

    @property
    def message(self):
        return self._message


class Processor:
    def __init__(self, savedir, socketio, loop, _config):
        self.savedir = savedir
        self.socketio = socketio
        self.loop = loop
        self.config = _config

        self.downloader = Downloader(self.savedir)


    async def process(self, songqueue, _title, **options):
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
            if self.config.enabledSources['youtube'] == False:
                print('Youtube as a source is disabled')
                return
            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=True)
            if not info:
                return
            if not all(info.get('entries', [])):
                return

            try:
                song_url = info['entries'][0]['webpage_url']
            except:
                print('Error - No search results for query - {}'.format(song_url), flush=True)
                return

            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=False)

            try:
                entry = PlaylistEntry(
                    song_url,
                    info['title'],
                    info['duration'],
                    options['requester']
                )
                songqueue.append(entry)
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
                if self.config.enabledSources['youtube-playlists'] == False:
                    print('Youtube playlists as a source are disabled')
                    return
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
                                    options['requester']
                                )
                                print('added from playlist - ' + playlist_info['title'], flush=True)
                                songqueue.append(entry)
                            except ExtractionError:
                                baditems += 1
                            except Exception as e:
                                baditems += 1
                                print('There was an error adding the song from playlist %s' %  entry_data['id'], flush=True)
                                print(e)
                        else:
                            baditems += 1

                        if items == self.config.maxPlaylistLength:
                            print('Playlist length longer than the allowed length', flush=True)
                            return

                except Exception:
                    print('Error handling playlist %s queuing.' % playlist_url, flush=True)
    # soundcloud and bandcamp
            elif info['extractor'].lower() in ['soundcloud:set', 'soundcloud:user', 'bandcamp:album']:
                if (self.config.enabledSources['soundcloud'] == False) and (info['extractor'].lower() in ['soundcloud:set', 'soundcloud:user']):
                    print('Soundcloud as a source is disabled')
                    return
                if (self.config.enabledSources['bandcamp'] == False) and (info['extractor'].lower() in ['bandcamp:album']):
                    print('Bandcamp as a source is disabled')
                    return
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
                                    options['requester']
                                )
                                print('added from playlist - ' + playlist_info['title'], flush=True)
                                songqueue.append(entry)
                            except ExtractionError:
                                baditems += 1
                            except Exception as e:
                                baditems += 1
                                print('There was an error adding the song from playlist %s' %  entry_data['id'], flush=True)
                                print(e)
                        else:
                            baditems += 1

                        if items == self.config.maxPlaylistLength:
                            print('Playlist length longer than the allowed length', flush=True)
                            return

                except Exception:
                    print('Error handling playlist %s queuing.' % playlist_url, flush=True)

            if baditems:
                print("Skipped %s bad entries" % baditems, flush=True)

            print('Added {}/{} songs from playlist'.format(items - baditems, items), flush=True)

####else if song is a url or other thing
        else:
            if self.config.enabledSources['wildcard'] == False:
                print('Wildcarding as a source is disabled')
                return
            info = await self.downloader.extract_info(self.loop, song_url, download=False, process=True)
            try:
                entry = PlaylistEntry(
                    song_url,
                    info['title'],
                    info['duration'],
                    options['requester']
                )
                songqueue.append(entry)
            except:
                print('Error with other option', flush=True)

        print('user input processed - ' + _title, flush=True)


    async def checkPlaylistURL(self, songqueue, title, **options):
        try:
            info = await self.downloader.extract_info(self.loop, title, download = False, process = False)
            entry = PlaylistEntry(
                        title,
                        info['title'],
                        info['duration'],
                        options['requester']
                    )
            songqueue.append(entry)
            print('added from playlist - ' + entry.title, flush=True)
        except:
            print('Server Playlist has a bad URL - ' + str(title), flush=True)


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