import socketio
import asyncio
import json


class PlaylistList:
    def __init__(self, _config, _socketio, _loop):
        self.config = _config
        self.socketio = _socketio
        self.loop = _loop

        self.loadFile()


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


    def getsongs(self, index, name):
        if self.playlists[index]['data']['name'] in name:
            return self.playlists[index]
        else:
            return {}