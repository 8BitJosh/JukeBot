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
#app.config.from_object(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
socketio = SocketIO(app, async_mode='eventlet')

#main webpage and form handler
@app.route("/")
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
    
@socketio.on('sent_song', namespace='/test')
def test_message(message):
    global playlist
    title = message['data']
    str = 'Queued Song - ' + title 
    
    print('receaved message submit - ' + title)
    if '&' in title:
        str = str + "\nIf you wanted to add a playlist use the full playlist page that has 'playlist' in the url"
        start_pos = title.find('&')
        msg = title[:start_pos]
        playlist.add(msg)
    else:
        playlist.add(title)
    
    print("user entered song - " + title)
    emit('response', {'data': str})

@socketio.on('song_skip', namespace='/test')
def skip_request():
    emit('response', {'data': 'Song Skipped'})
    global web_inputs
    web_inputs.put('skip')
    
@socketio.on('song_shuffle', namespace='/test')
def shuffle_request():
    emit('response', {'data': 'Songs Shuffled'})
    print("shuffled ?")
    global web_inputs
    web_inputs.put('shuffle')

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    global playlist
    endmsg = playlist.getPlaylist()
    if(endmsg == ''):
        endmsg = "There is currently nothing in the playlist"
    emit('sent_playlist', {'data': endmsg}, namespace = '/test')
    emit('my_pong')

#Thread constantly looping to playsong / process the current command
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

#function to run for webpage thread
#def start_web():
    #app.run(host = '0.0.0.0', port=80, debug = False, threaded = True, use_reloader = False)
#    socketio.run(app, debug = True)
    
#create threads for other things
t = threading.Thread(target = player_update).start()
#p = threading.Thread(target = start_web).start()
socketio.run(app, debug = True, host = '0.0.0.0', port=80)