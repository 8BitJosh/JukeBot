import subprocess
import os
import time
import traceback

class Player:
#play song located at path
#might add pipe stuff? for stdin commands idk if this will work - have to give it a try
    def __init__(self):
        pass

# start playing song at path
    def play(self, _path):
        self.path = _path
        self.p = subprocess.Popen(
                            ['ffplay', '-nodisp', '-autoexit', self.path],
                            #shell = True
                            stdout=subprocess.DEVNULL, 
                            stdin=subprocess.PIPE, 
                            stderr=subprocess.STDOUT
                            )
    
#check if the song is still running
    def running(self):
        try:
            if self.p.poll() is None:
                return True
            else:
                self.path = ''
                return False
        except:
            return False
    
#stop current song and cancel playback
    def stop(self):
        if self.running():
            self.p.kill()
            self.delete_file()
            self.path = ''
        else:
            print("Unable to skip - no song playing")
            
#delete the file in the current path
    def delete_file(self):
        for x in range(30):
            try:
                os.unlink(self.path)
                break

            except PermissionError as e:
                if e.winerror == 32:  # File is in use
                    time.sleep(0.25)

            except Exception as e:
                traceback.print_exc()
                print("Error trying to delete " + self.path)
                break
        else:
            print("[Config:SaveVideos] Could not delete file {}, giving up and moving on".format(
                os.path.relpath(self.path)))
