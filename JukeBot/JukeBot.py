import time
import threading
import json

from player import Player
from playlist import Playlist
from utils import configCheck

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

with open('config.json') as file:
    uncheckedConfig = json.load(file)

config = configCheck(uncheckedConfig)

playlist = Playlist(config)
player = Player(config)

app = Flask(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
socketio = SocketIO(app, async_mode='eventlet')

player.multicast(True) 

@app.route("/")
def index():
    print("Client loaded page", flush=True)
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connected', namespace='/main')
def connect_playlist(msg):
    global playlist
    global player
    print("Client socket connected - " + request.remote_addr, flush=True)
    emit('sent_playlist', playlist.getPlaylist())
    emit('duration', player.getDuration(), broadcast=True)
    emit('volume_set', {'vol': player.getVolume()}, broadcast = True)


@socketio.on('sent_song', namespace='/main')
def song_received(message):
    global playlist
    title = message['data']

    if title != '':
        str = 'Queued Song - ' + title
        if '&' in title:
            str = str + '\nIf you wanted to add a playlist use the full playlist page that has "playlist" in the url'
            start_pos = title.find('&')
            msg = title[:start_pos]
        else:
            msg = title

        print(request.remote_addr + ' submitted - ' + title, flush=True)
        p = threading.Thread(target = playlist.process, args = (msg,)).start()
    else:
        str = 'Enter a Song Name'
    emit('response', {'data': str})


@socketio.on('button', namespace='/main')
def button_handler(msg):
    global playlist
    global player
    command = msg['data']

    if command == 'skip':
        emit('response', {'data': 'Song Skipped'})
        print(request.remote_addr + ' Skipped song', flush=True)
        player.stop()
    elif command == 'shuffle':
        emit('response', {'data': 'Songs Shuffled'})
        print(request.remote_addr + ' shuffled playlist', flush=True)
        playlist.shuff()
    elif command == 'clear':
        playlist.clearall()
        print(request.remote_addr + ' cleared all of playlist', flush=True)
        emit('response', {'data': 'Playlist Cleared'})
    elif command == 'pause':
        if player.isPaused():
            print(request.remote_addr + ' Resumed the song', flush=True)
            emit('response', {'data': 'Song Resumed'})
            emit('pause_button', {'data': 'Pause'}, broadcast=True)
            player.pause()
        elif player.running():
            print(request.remote_addr + ' Paused the song', flush=True)
            emit('response', {'data': 'Song Paused'})
            emit('pause_button', {'data': 'Resume'}, broadcast=True)
            player.pause()


@socketio.on('volume', namespace='/main')
def set_volume(msg):
    global player
    vol = int(msg['vol'])
    player.setVolume(vol)
    print(request.remote_addr + ' set volume to ' + str(vol), flush = True)
    emit('volume_set', {'vol': vol}, broadcast = True)


@socketio.on('delete', namespace='/main')
def delete_song(msg):
    global playlist
    title = msg['title']
    index = msg['data']
    print(request.remote_addr + ' removed index ' + str(index) + ' title = ' + title, flush=True)

    playlist.remove(index, title)

    s = 'Removed song from playlist - ' + title
    emit('response', {'data': s})


@socketio.on('ping', namespace='/main')
def return_playlist():
    global playlist
    if playlist.updated():
        emit('sent_playlist', playlist.getPlaylist(), broadcast=True)
    global player
    # if player.newsong():
    emit('duration', player.getDuration(), broadcast=True)


# Thread constantly looping to playsong / process the current command
def player_update():
    global playlist
    global player

    while True:
        p = threading.Thread(target = playlist.download_next).start()

        if not player.running() and not player.isPaused():
            if not playlist.empty():
                song = playlist.get_next()
                if song.dir != '':
                    player.play(song)

        time.sleep(1)

# create threads and start webserver
t = threading.Thread(target = player_update).start()
socketio.run(app, debug=False, host='0.0.0.0', port=config['main']['webPort'])
