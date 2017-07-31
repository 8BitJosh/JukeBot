import subprocess
import os
import time
import traceback
from utils import delete_file

class Player:
#play song located at path
#might add pipe stuff? for stdin commands idk if this will work - have to give it a try
    def __init__(self):
        pass

# start playing song at path
    def play(self, _path):
        self.path = _path
        self.p = subprocess.Popen(
                            ['avplay', '-nodisp', '-autoexit', self.path],
                            #shell = True
                            stdout=subprocess.DEVNULL, 
                            stdin=subprocess.PIPE, 
                            stderr=subprocess.STDOUT
                            )
        print("playing - " + self.path)
    
#check if the song is still running
    def running(self):
        try:
            if self.p.poll() is None:
                return True
            else:
                if self.path != '' and os.path.exists(self.path):
                    delete_file(self.path)
                self.path = ''
                return False
        except: # causes error before first song as no process is playing
            return False
    
#stop current song and cancel playback
    def stop(self):
        if self.running():
            self.p.kill()
            delete_file(self.path)
            self.path = ''
        else:
            print("Unable to skip - no song playing")


