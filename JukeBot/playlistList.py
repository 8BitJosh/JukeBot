import socketio
import asyncio
import json

from process import Processor


class PlaylistList:
    def __init__(self, _config, _socketio, _loop):
        self.config = _config
        self.socketio = _socketio
        self.loop = _loop
        self.savedir = self.config['main']['songcacheDir']

        self.loadFile()
        self.processor = Processor(self.savedir, self.socketio, self.loop)


    def loadFile(self):
        try:
            with open('savedPlaylists.json', 'r') as file:
                self.playlists = json.load(file)
        except:
            with open('savedPlaylists.json', 'w') as file:
                json.dump({}, file)
            self.loadFile()


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
        self.playlists[name] = songs
        self.saveFile()
        self.loadFile()
        await self.socketio.emit('playlistList', self.getPlaylists(), namespace='/main', broadcast = True)


    async def newPlaylist(self, name):
        data = {'name': name, 'dur' : 0}
        self.playlists[name] = {}
        self.playlists[name]['data'] = data
        self.saveFile()
        self.loadFile()
        await self.socketio.emit('playlistList', self.getPlaylists(), namespace='/main', broadcast = True)


    async def addSong(self, playlistName, title):
        pass


    async def removeSong(self, playlistName, index, title):
        pass


    async def beingModified(self, playlistName):
        pass


