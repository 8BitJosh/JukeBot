import vlc
import os
from utils import delete_file

import asyncio

class Player:
    # create the player member
    def __init__(self, _config, _socketio, _loop):
        self.config = _config
        self.socketio = _socketio
        self.loop = _loop

        self.path = ''
        self.dur = 0
        self.instance = vlc.Instance("--no-video --aout=alsa")
        #Create a MediaPlayer with the default instance
        self.player = self.instance.media_player_new()
        self.setVolume(self.config['player']['defaultVol'])

# start playing song at path
    async def play(self, _song):
        self.path = _song.dir
        self.dur = int(_song.duration)
        media = self.instance.media_new(self.path)
        self.player.set_media(media)
        self.player.play()
        await self.sendDuration()
        print("playing - " + self.path, flush=True)

# has a new song started playing
    def newsong(self):
        if self.newSong:
            self.newSong = False
            return True
        else:
            return False

# get song duration and current position
    async def sendDuration(self):
        durData = {}

        durData['length'] = self.dur

        if self.running() or self.isPaused():
            durData['position'] = int(self.player.get_time()/1000)
        else:
            durData['position'] = 0

        if self.isPaused() or not self.running():
            durData['paused'] = 1
        else:
            durData['paused'] = 0

        await self.socketio.emit('duration', durData, namespace='/main')

# check if the song is still running
    def running(self):
        if ( self.player.get_state() == vlc.State.Playing ) or ( self.player.get_state() == vlc.State.Opening ):
            return True
        else:
            if ( self.player.get_state() == vlc.State.Paused ) or ( self.player.get_state() == vlc.State.Stopped ):
                return False
            self.player.stop()
            if self.path != '' and os.path.exists(self.path):
                print("deleting", flush=True)
                delete_file(self.path)
            self.path = ''
            self.dur = 0
            return False

# stop current song and cancel playback
    def stop(self):
        if self.running():
            self.player.stop()
            delete_file(self.path)
            self.path = ''
            self.dur = 0
        else:
            print("Unable to skip - no song playing", flush=True)

# pause/resume the current song
    def pause(self):
        self.player.pause()

# check for a paused song
    def isPaused(self):
        if ( self.player.get_state() == vlc.State.Paused ):
            return True
        return False

# set the playback volume
    def setVolume(self, _volume):
        self.player.audio_set_volume(_volume)
        self.volume = _volume

# get the current playback volume
    def getVolume(self):
        if self.player.audio_get_volume() == -1:
            return self.volume
        else:
            self.volume = self.player.audio_get_volume()
            return self.volume
