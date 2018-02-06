import os
import shutil
import datetime

import asyncio

from random import shuffle
from utils import PlaylistEntry, delete_file

class Playlist:
    def __init__(self, _config, _socketio, loop, _processor):
        self.config = _config
        self.socketio = _socketio
        self.loop = loop
        self.processor = _processor

        self.songqueue = []
        self.currently_play = ''

        self.savedir = self.config.songcacheDir
        if os.path.exists(self.savedir):
            shutil.rmtree(self.savedir)
        os.makedirs(self.savedir)



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
            return PlaylistEntry('', 'title', 0)

        self.currently_play = "[" + str(datetime.timedelta(seconds=int(self.songqueue[0].duration))) + "] " + self.songqueue[0].title
        song = self.songqueue[0]
        print("Removed from to play queue - " + self.songqueue[0].title)
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


    async def getQueue(self):
        queue = {}
        x = 0
        length = 0
        for song in self.songqueue:
            s = {'url': song.url, 'title': song.title, 'dur': song.duration}
            length += song.duration
            queue[x] = s
            x += 1
        queue['data'] = {'name': '', 'dur': length}
        return queue


    async def remove(self, _index, _title):
        index = _index - 1
        start = _title.find(']') + 2
        title = _title[start:]

        try:
            playlistTitle = self.songqueue[index].title
            del_path = self.songqueue[index].dir
        except IndexError:
            print('More than one user removed a song at the same time')
            return

        if title.strip() == playlistTitle.strip():
            del self.songqueue[index]
            await self.sendPlaylist()
            if del_path != '':
                delete_file(del_path)
        else:
            print('More than one user removed a song at the same time')
            return

    async def clearall(self):
        while len(self.songqueue):
            if self.songqueue[0].dir != '':
                delete_file(self.songqueue[0].dir)
            del self.songqueue[0]

        self.songqueue.clear()
        await self.sendPlaylist()


    async def addPlaylist(self, songs, _requester):
        for song in songs:
            if 'data' not in song:
                await self.processor.checkPlaylistURL(self.songqueue, songs[song]['url'], requester=_requester)
                    

    async def process(self, _title, _requester):
        await self.processor.process(self.songqueue, _title, requester=_requester)
        await self.sendPlaylist()
    

    #download next non downloaded song
    async def download_next(self):
        for things in self.songqueue:
            if things.downloaded == False:
                if things.downloading == True:
                    break
                things.downloading = True
                things.dir = await self.processor.download_song(things)
                things.downloaded = True
                break


