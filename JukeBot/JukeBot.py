import subprocess
import re
import youtube_dl
import os
import sys
import time
import traceback
import threading
import datetime
import re
import unicodedata
import queue
from random import shuffle
from player import Player

savedir = "playlist"

if not os.path.exists(savedir):
    os.makedirs(savedir)
    
volume = 0.15

commands = queue.Queue()
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
    global commands
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
        commands.put('skip')
    elif msg.lower() == 'pause':
        commands.put('pause')
    elif msg.lower() == 'resume':
        commands.put('resume')
    elif msg.lower() == 'exit':
        commands.put('exit')
    elif msg.lower() == 'shuffle':
        shuffle(playlist)
    elif 'volume' in msg.lower():
        substrStart = msg.find('volume') + 7
        msg = msg[substrStart: ]
        msg.strip()
        try:
            volume = int(msg)
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
    endMsg = unicodedata.normalize('NFKD', message).encode('ascii', 'ignore').decode('ascii')
    endMsg = re.sub('[^\w\s-]', '', endMsg).strip().lower()
    endMsg = re.sub('[-\s]+', '-', endMsg)
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
        currentlyPlaying = 'Now: ['+ str(datetime.timedelta(seconds=info['duration'])) + ']  ' + title + '\n'
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
def playlist_update():
    isPlaying = False
    global volume
    global currentlyPlaying
    
    option = 'none'
    count = 0
    
    while count != -1:
        if commands.empty():
            option = 'none'
        else:
            option = commands.get()
        
        if isPlaying is False:
            if playlist:
                thing = playlist[0]
                try:
                    path = download_song(thing)
                    if path != 'bad_path':
                        player = Player(path)
                        isPlaying = True
                    while thing in playlist: playlist.remove(thing)
                except:
                    while thing in playlist: playlist.remove(thing)
        if option == 'skip':
            player.stop()
            currentlyPlaying = ''
            isPlaying = False
        elif option == 'exit':
            player.stop()
            count = -1
        else:
            time.sleep(0.25)

#create threads for other things
try:
    t = threading.Thread(target = playlist_update).start()
except Exception:
    print("fail to start loop")
finally:
    run = 1
    while run == 1:
        message = input("Input Command - ")
        on_message(message)
        if message == 'exit':
            while not commands.empty():
                time.sleep(1)
            run = 0