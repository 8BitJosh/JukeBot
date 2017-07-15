import subprocess
import os

#vce.create_ffmpeg_player(path, options='''-filter:a "volume={}"'''.format(volume))
# ^^^ original music bot help for filter/volume
#-af dynaudnorm       <- normalization filter ?

class Player:
#play song located at path kill current song first if running
#might add pipe stuff? for stdin commands
    def __init__(self, path):
        self.p = subprocess.Popen(
                            ['ffplay', '-nodisp', '-autoexit', path],
                            #shell = True
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT)

        if self.p.poll() is None:
            print("poll true")
    
#check if the song is still running
    def running(self):
        #print("is it running")
        #for line in iter(self.p.stdout.readline, b''):
        #    print( '>>> {}'.format(line))
        return True
        #process.poll() to check if subprocess is still running
    
#stop current song and cancel playback
    def stop(self):
        print("stop")
    
#pause the current song could pipe stdin to ffmpeg 'p' pauses/resumes
    def pause(self):
        print("pause")
    
#resume the current song if it has been resumed
    def resume(self):
        print("resume")

# Get duration with ffprobe
#   ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -sexagesimal filename.mp3
# This is also how I fix the format checking issue for now
# ffprobe -v quiet -print_format json -show_format stream