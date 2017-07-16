import subprocess
import os
import time

#to delete file after finished with it
#os.remove("filename.mp3")

class Player:
#play song located at path kill current song first if running
#might add pipe stuff? for stdin commands idk if this will work - have to give it a try
    def __init__(self, _path):
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
        if self.p.poll() is None:
            return True
        else:
            print("Finished")
            return False      
    
#stop current song and cancel playback
    def stop(self):
        self.p.kill()
        print("stop")
        time.sleep(1)
        if os.access(self.path, os.F_OK):
            try:
                os.remove(self.path)
            except:
                print("file cant removed")
        else:
            print("File already Deleted")

#pause the current song could pipe stdin to ffmpeg 'p' pauses/resumes
    def pause(self):
        print("pause")
    
#resume the current song if it has been resumed
    def resume(self):
        print("resume")
