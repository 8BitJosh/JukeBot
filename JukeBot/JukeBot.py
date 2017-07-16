import subprocess
import re
import youtube_dl
import os
import sys
import time
import traceback
import threading
from random import shuffle
from player import Player

savedir = "playlist"
if not os.path.exists(savedir):
    os.makedirs(savedir)
    
option = 'none'
isPlaying = False

playlist = []
currentlyPlaying = ''

options = {
    'format': 'bestaudio/best',
    'extractaudio' : True,
    'audioformat' : "mp3",
    'outtmpl': '%(id)s',
    'noplaylist' : True,
    'nocheckcertificate' : True,
    'ignoreerrors' : True,
    'quiet' : True,
    'no_warnings' : True,
    'default_search': 'ytsearch',
    }

#called when user enters a command and processes it acordingly
def on_message(message):
    global option
    global volume
    
    msg = message
    msg.strip()
    if msg.lower() == 'playlist':
        endmsg = currentlyPlaying
        endmsg = endmsg + getPlaylist()
        if(endmsg == ''):
            print("There is currently nothing left in the playlist")
        else:
            print(endmsg)
    elif msg.lower() == 'skip':
        option = 'skip'
    elif msg.lower() == 'shuffle':
        shuffle(playlist)
    elif msg.lower() == 'pause':
        option = 'pause'
    elif msg.lower() == 'resume':
        option = 'resume'
    elif 'volume' in msg.lower():
        substrStart = msg.find('volume') + 7
        msg = msg[substrStart: ]
        msg.strip()
        try:
            volume = msg
        except:
            print("thats not a number please use a number")
    elif 'play' in msg.lower():
        substrStart = msg.find('play') + 5
        msg = msg[substrStart: ]
        msg.strip()
        playlist.append(msg)
        fixPlaylist()
    else:
        print("Invalid Command")

#reformat the titles so the titles are suitable for windows file names
def do_format(message):
    replacements = ( ('4','a'), ('3','e'), ('1','l'), ('0','o'), ('7','t') )
    endMsg = re.sub('À|à|Á|á|Â|â|Ã|ã|Ä|ä', 'a', message)
    endMsg = re.sub('È|è|É|é|Ê|ê|Ë|ë', 'e', endMsg)
    endMsg = re.sub('Ì|ì|Í|í|Î|î|Ï|ï', 'i', endMsg)
    endMsg = re.sub('Ò|ò|Ó|ó|Ô|ô|Õ|õ|Ö', 'o', endMsg)
    endMsg = re.sub('Ù|ù|Ú|ú|Û|û|Ü|ü', 'u', endMsg)
    endMsg = re.sub('Ý|ý|Ÿ|ÿ', 'y', endMsg)
    endMsg = re.sub('Ñ|ñ', 'n', endMsg)
    for old, new in replacements:
        endMsg = endMsg.replace(old, new)
    endMsg = re.sub('[^0-9a-zA-Z]+', '', endMsg)
    endMsg = re.sub(r'([a-z])\1+', r'\1', endMsg)
    return endMsg

#fix the urls / remove bad items from the playlist that cant be found on yt
def fixPlaylist():
    for things in playlist:
        error_options = {
                'format': 'bestaudio/best',
                'extractaudio' : True,
                'audioformat' : "mp3",
                'outtmpl': '%(id)s',
                'noplaylist' : True,
                'nocheckcertificate' : True,
                'default_search': 'ytsearch'
            }
        ydl = youtube_dl.YoutubeDL(error_options)
        try:
            info = ydl.extract_info(things, download=False)
        except Exception as e:
            while things in playlist: playlist.remove(things)
            
def length(path):
    length = subprocess.check_output(['ffprobe', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', '-sexagesimal', path])   
    length = length.decode("utf-8")
    millisStart = length.find('.')
    length = length[ :millisStart]
    return length
    
#itterate through playlist get the title from youtube url search and print to screen
def getPlaylist():
    endmsg = ''
    count = 0
    for things in playlist:
        song_url = things.strip()
        ydl = youtube_dl.YoutubeDL(options)

        try:
            info = ydl.extract_info(song_url, download = False, process = False)
        except Exception:
            print("error")
            pass
        
        if info.get('url', '').startswith('ytsearch'):
            info = ydl.extract_info(song_url, download = False, process = True)
        
            if not all(info.get('entries', [])):
                return
            
            song_url = info['entries'][0]['webpage_url']
            info = ydl.extract_info(song_url, download = False, process = False)

        try:
            title = info['title']
        except:
            print("oh no url YT error again")
        count += 1
        endmsg = endmsg + str(count) + ": " + title + " \n"
    return endmsg

#download song from url or search term and return the save path of the file
def download_song(unfixedsongURL):
    global currentlyPlaying

    song_url = unfixedsongURL.strip()
    ydl = youtube_dl.YoutubeDL(options)

    try:
        info = ydl.extract_info(song_url, download = False, process = False)
    except Exception:
        print("error")
        pass
        
    if not info:
        print("Ths video cannot be played")
        return
        
    if info.get('url', '').startswith('ytsearch'):
        info = ydl.extract_info(song_url, download = False, process = True)
        
        if not all(info.get('entries', [])):
            return
            
        song_url = info['entries'][0]['webpage_url']
        info = ydl.extract_info(song_url, download = False, process = False)

    try:
        title = info['title']
        currentlyPlaying = 'Now: ' + title + '\n'
        title = do_format(title)
        savepath = os.path.join(savedir, "%s.mp3" % (title))
    except Exception as e:
        print("Can't access song! %s\n" % traceback.format_exc())
        return 'bad_path'

    try:
        os.stat(savepath)
        return savepath
    except OSError:
        try:
            result = ydl.extract_info(song_url, download=True)
            os.rename(result['id'], savepath)
            return savepath
        except Exception as e:
            print ("Can't download audio! %s\n" % traceback.format_exc())
            return 'bad_path'

#Thread constantly looping to playsong / process the current command
#update this to use a vector for the commands so that multiple people can do things
#    and commands get queued
def playlist_update():
    global isPlaying
    global option
    global volume
    global currentlyPlaying
    
    count = 0
    while count != -1:
        if isPlaying is False and option != 'pause':
            if playlist:
                thing = playlist[0]
                try:
                    path = download_song(thing)
                    if path != 'bad_path':
                        player = Player(path)
                        isPlaying = True
                        while thing in playlist: playlist.remove(thing)
                        option = 'sleep'
                    else:
                        while thing in playlist: playlist.remove(thing)
                except:
                    while thing in playlist: playlist.remove(thing)
        if option == 'sleep' or option == 'skip':
            while option != 'skip' and player.running():
                if option == 'pause':
                    player.pause()
                elif option == 'resume':
                    player.resume()
                    option = 'sleep'
                else:
                    time.sleep(1)
            player.stop()
            option = 'none'
            currentlyPlaying = ''
            isPlaying = False
        elif option == 'pause':
            player.pause()
            while option != 'resume':
                time.sleep(1)
            player.resume()
        else:
           time.sleep(1)

#create threads for other things
try:
    t = threading.Thread(target = playlist_update).start()
except Exception:
    print("fail to start loop")
finally:
    while True:
        message = input("Input Command - ")
        on_message(message)
