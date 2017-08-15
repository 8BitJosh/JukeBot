import time
import threading
import queue

from player import Player
from playlist import Playlist

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

web_inputs = queue.Queue()
playlist = Playlist()
player = Player()

app = Flask(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
socketio = SocketIO(app, async_mode='eventlet')


@app.route("/")
def index():
    print("Client connected - " + request.remote_addr, flush=True)
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connected', namespace='/main')
def connect_playlist(msg):
    global playlist
    emit('sent_playlist', playlist.getPlaylist())
    emit('duration', player.getDuration(), broadcast=True)


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
            playlist.add(msg)
        else:
            playlist.add(title)

        print(request.remote_addr + ' submitted - ' + title, flush=True)
    else:
        str = 'Enter a Song Name'
    emit('response', {'data': str})


@socketio.on('button', namespace='/main')
def button_handler(msg):
    global web_inputs
    global playlist
    global player
    command = msg['data']

    if command == 'skip':
        emit('response', {'data': 'Song Skipped'})
        print(request.remote_addr + ' Skipped song', flush=True)
        web_inputs.put('skip')
    elif command == 'shuffle':
        emit('response', {'data': 'Songs Shuffled'})
        print(request.remote_addr + ' shuffled playlist', flush=True)
        web_inputs.put('shuffle')
    elif command == 'clear':
        playlist.clearall()
        print(request.remote_addr + ' cleared all of playlist', flush=True)
        emit('response', {'data': 'Playlist Cleared'})
    elif command == 'pause':
        print(request.remote_addr + ' paused the song', flush=True)
        emit('response', {'data': 'Song Paused'})
        web_inputs.put('pause')
        
        #if player.isPaused():
        #    emit('response', {'data': 'Song Resumed'})
        #    web_inputs.put('pause')
        #elif player.running():
        #    emit('response', {'data': 'Song Paused'})
        #    web_inputs.put('pause')


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
    global web_inputs
    global playlist
    global player

    while True:
        option = 'none'
        if not web_inputs.empty():
            msg = web_inputs.get()
            print('command called - ' + msg, flush=True)
            if msg == 'skip':
                option = 'skip'
            elif msg == 'shuffle':
                playlist.shuff()
            elif msg == 'pause':
                option = 'pause'
        else:
            playlist.process()
            playlist.download_next()

        if not player.running():
            if not playlist.empty():
                song = playlist.get_next()
                if song.dir != '':
                    player.play(song)

        if option == 'skip':
            player.stop()
        elif option == 'pause':
            player.pause()
        else:
            time.sleep(0.1)

# create threads and start webserver
t = threading.Thread(target = player_update).start()
socketio.run(app, debug=False, host='0.0.0.0', port=80)
