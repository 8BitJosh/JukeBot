import subprocess
import youtube_dl

import os, sys
import time
import traceback
import threading
import datetime

#import logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

import re
import unicodedata

import queue
from random import shuffle
from player import Player

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

savedir = "playlist"

if not os.path.exists(savedir):
    os.makedirs(savedir)
    
volume = 0.15

web_inputs = queue.Queue()
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

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
class ReusableForm(Form):
    title = TextField('Title:', validators=[validators.required()])
 
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    global web_inputs
 
    print(form.errors)
    if request.method == 'POST':
        title=request.form['title']
 
        if form.validate():
            web_inputs.put(title)
            flash('Added Song - ' + title)
        else:
            flash('Error: All the form fields are required. ')
 
    return render_template('index.html', form=form)

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
    global web_inputs
    
    option = 'none'
    count = 0
    
    while count != -1:
        option = 'none'
        if not web_inputs.empty():
            msg = web_inputs.get()
            msg.strip()
            print(msg)
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
            elif 'volume' in msg.lower():
                substrStart = msg.find('volume') + 7
                msg = msg[substrStart: ]
                msg.strip()
                try:
                    volume = int(msg)
                except:
                    print("thats not a number please use a number")
            else:
                playlist.append(msg)
                fixPlaylist()
        
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
            time.sleep(0.1)

def start_web():
    app.run(host = '0.0.0.0', port=80, debug = False, threaded = True, use_reloader = False)
    
#create threads for other things
t = threading.Thread(target = playlist_update).start()
p = threading.Thread(target = start_web).start()