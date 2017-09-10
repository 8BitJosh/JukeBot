import socketio
import asyncio
import json
import os

from process import Processor


class PlaylistList:
    def __init__(self, _config, _socketio, _loop):
        self.config = _config
        self.socketio = _socketio
        self.loop = _loop
        self.savedir = self.config['main']['songcacheDir']

        if not os.path.isfile('savedPlaylists.json'):
            with open('savedPlaylists.json', 'w') as file:
                json.dump({}, file)
        self.loadFile()

        self.processor = Processor(self.savedir, self.socketio, self.loop)


    def loadFile(self):
        with open('savedPlaylists.json', 'r') as file:
            self.playlists = json.load(file)


    def saveFile(self):
        with open('savedPlaylists.json', 'w') as file:
            json.dump(self.playlists, file)


    def getPlaylists(self):
        msg = {}
        for index in self.playlists:
            msg[index] = self.playlists[index]['data']
        return msg


    def getsongs(self, name):
        try:
            songs = self.playlists[name]
        except:
            songs = {}
        return songs


    async def addqueue(self, songs):
        name = songs['data']['name']
        
        name = self.checkUnique(name)
        songs['data']['name'] = name

        self.playlists[name] = songs
        self.saveFile()
        self.loadFile()
        await self.socketio.emit('playlistList', self.getPlaylists(), namespace='/main', broadcast = True)


    async def newPlaylist(self, name):
        name = self.checkUnique(name)
        data = {'name': name, 'dur' : 0}
        self.playlists[name] = {}
        self.playlists[name]['data'] = data
        self.saveFile()
        self.loadFile()
        await self.socketio.emit('playlistList', self.getPlaylists(), namespace='/main', broadcast = True)


    async def addSong(self, playlistName, title):
        entry = []
        await self.processor.process(entry, title, 'playlist')

        song = {'url': entry[0].url, 'title': entry[0].title, 'dur': entry[0].duration}

        index = len(self.playlists[playlistName]) - 1
        self.playlists[playlistName][index] = song
        self.saveFile()
        self.loadFile()

    async def removeSong(self, playlistName, index, title):
        temp = {}
        ind = 0
        duration = 0
        for song in self.playlists[playlistName]:
            if song == str(index) and self.playlists[playlistName][song]['title'] == title:
                print('Song removed from playlist - ' + playlistName + ' - at index - ' + str(index))
                pass
            elif song == 'data':
                temp['data'] = self.playlists[playlistName][song]
            else:
                temp[ind] = self.playlists[playlistName][song]
                duration += self.playlists[playlistName][song]['dur']
                ind += 1
        temp['data']['dur'] = duration
        self.playlists[playlistName] = temp
        self.saveFile()
        self.loadFile()

    async def beingModified(self, playlistName):
        pass

    def checkUnique(self, name):
        append = 1;
        dupe = True
        test = name
        while dupe:
            dupe = False
            for names in self.playlists:
                if self.playlists[names]['data']['name'] == test:
                    dupe = True
                    test = name + '-' + str(append)
                    append += 1
        return test