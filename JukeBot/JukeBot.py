import time
import threading
import queue

from player import Player
from playlist import Playlist

from flask import Flask, render_template, flash, request, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
   
web_inputs = queue.Queue()
playlist = Playlist()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
 
class ReusableForm(Form):
    title = TextField('Title:', validators=[validators.required()])

#main webpage and form handler
@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)
    global web_inputs
    global playlist
 
    print(form.errors)
    if request.method == 'POST':
        title=request.form['title']
        
        if 'submit' in request.form:
            if form.validate():
                if '&' in title:
                    flash("If you wanted to add a playlist use the full playlist page that has 'playlist' in the url")
                    start_pos = title.find('&')
                    msg = title[:start_pos]
                    playlist.add(msg)
                else:
                    playlist.add(title)
                flash('Queued Song - ' + title)
                print("user entered song - " + title)
        elif 'skip' in request.form:
            flash('Song Skipped')
            web_inputs.put('skip')
        elif 'shuffle' in request.form:
            flash('Playlist Shuffled')
            web_inputs.put('shuffle')

    return render_template('index.html', form=form)

#ajax call to return playlist in json format
@app.route('/data')
def data():
    endmsg = playlist.getPlaylist()
    if(endmsg == ''):
        return jsonify("There is currently nothing in the playlist")
    else:
        return jsonify(endmsg)

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
def start_web():
    app.run(host = '0.0.0.0', port=80, debug = False, threaded = True, use_reloader = False)
    
#create threads for other things
t = threading.Thread(target = player_update).start()
p = threading.Thread(target = start_web).start()