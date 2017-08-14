import subprocess
import os
import time
from utils import delete_file


class Player:
    # create the player member
    def __init__(self):
        self.path = ''
        self.dur = 0

# start playing song at path
    def play(self, _song):
        self.path = _song.dir
        self.dur = _song.duration
        self.p = subprocess.Popen(
                            ['avplay', '-nodisp', '-autoexit', self.path],
                            #shell = True
                            stdout=subprocess.DEVNULL, 
                            stdin=subprocess.PIPE, 
                            stderr=subprocess.STDOUT
                            )
        self.startTime = time.time()
        self.newSong = True
        print("playing - " + self.path)

# has a new song started playing
    def newsong(self):
        if self.newSong:
            self.newSong = False
            return True
        else:
            return False

# get song duration and current position
    def getDuration(self):
        durData = {}

        durData['dur'] = self.dur

        if self.running():
            durData['pos'] = int(time.time() - self.startTime)
        else:
            durData['pos'] = 0

        return durData

# check if the song is still running
    def running(self):
        try:
            if self.p.poll() is None:
                return True
            else:
                if self.path != '' and os.path.exists(self.path):
                    delete_file(self.path)
                self.path = ''
                self.dur = 0
                return False
        except Exception as e:
            # causes error before first song as no process is playing
            return False

# stop current song and cancel playback
    def stop(self):
        if self.running():
            self.p.kill()
            delete_file(self.path)
            self.path = ''
            self.dur = 0
        else:
            print("Unable to skip - no song playing")
