import time
import threading
import queue

from player import Player
from playlist import Playlist

from flask import Flask, render_template, flash, session, request
from flask_socketio import SocketIO, emit
import eventlet

web_inputs = queue.Queue()
playlist = Playlist()

app = Flask(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
socketio = SocketIO(app, async_mode='eventlet')

#### handlers for main suggestion page
@app.route("/")
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
    
@socketio.on('sent_song', namespace='/main')
def song_received(message):
    global playlist
    title = message['data']
    print('receaved message submit - ' + title)
    
    if title != '':
        str = 'Queued Song - ' + title 
        if '&' in title:
            str = str + "\nIf you wanted to add a playlist use the full playlist page that has 'playlist' in the url"
            start_pos = title.find('&')
            msg = title[:start_pos]
            playlist.add(msg)
        else:
            playlist.add(title)
    
        print("user entered song - " + title)
    else:
        str = 'Enter a Song Name'
    emit('response', {'data': str})

@socketio.on('song_skip', namespace='/main')
def skip_request():
    emit('response', {'data': 'Song Skipped'})
    global web_inputs
    web_inputs.put('skip')
    
@socketio.on('song_shuffle', namespace='/main')
def shuffle_request():
    emit('response', {'data': 'Songs Shuffled'})
    print("shuffled ?")
    global web_inputs
    web_inputs.put('shuffle')

@socketio.on('connected', namespace='/main')
def connect_playlist(msg):
    global playlist
    emit('sent_playlist', playlist.getPlaylist())

@socketio.on('ping', namespace='/main')
def return_playlist():
    global playlist
    if playlist.updated():
        emit('sent_playlist', playlist.getPlaylist(), broadcast=True)
        
@socketio.on('delete', namespace='/main')
def delete_song(msg):
    global playlist
    print('user sent to remove = ' + msg['title'])
    playlist.remove(msg['data'])
    print("Removed song from playlist at position = " + str(msg['data'] - 1))
    
@socketio.on('clear_playlist', namespace='/main')
def clear_playlist():
    global playlist
    playlist.clearall()
    print('cleared all of playlist')
    

#### Thread constantly looping to playsong / process the current command
def player_update():
    global web_inputs
    global playlist
    player = Player()
    
    while True:
        option = 'none'
        if not web_inputs.empty():
            msg = web_inputs.get()
            print("command called - " + msg)
            if msg == 'skip':
                option = 'skip'
            elif msg == 'shuffle':
                playlist.shuff()
        else:
            playlist.process()
            playlist.download_next()
               
        if not player.running():
            if not playlist.empty():
                path = playlist.get_next()
                if path != '':
                    player.play(path)

        if option == 'skip':
            player.stop()
        else:
            time.sleep(0.1)

####create threads and start webserver
t = threading.Thread(target = player_update).start()
socketio.run(app, debug = True, host = '0.0.0.0', port=80)