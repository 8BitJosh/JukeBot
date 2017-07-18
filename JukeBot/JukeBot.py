import os, sys
import time
import threading

import queue

from player import Player
from playlist import Playlist

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
   
web_inputs = queue.Queue()
playlist = Playlist()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '925c12c538c41b29bb46162ab603831bba8e34b7211fc72c'
 
class ReusableForm(Form):
    title = TextField('Title:', validators=[validators.required()])
 
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
                playlist.add(title)
                flash('Added Song - ' + title)
            else:
                flash('Error: All the form fields are required. ')
        elif 'skip' in request.form:
            web_inputs.put('skip')
        elif 'shuffle' in request.form:
            web_inputs.put('shuffle')
        elif 'playlist' in request.form:
            endmsg = playlist.getPlaylist()
            if(endmsg == ''):
                flash("There is currently nothing left in the playlist")
            else:
                flash(endmsg)

    return render_template('index.html', form=form)

#Thread constantly looping to playsong / process the current command
def player_update():
    isPlaying = False
    global web_inputs
    global playlist
    
    option = 'none'
    count = 0
    
    while count != -1:
        option = 'none'
        if not web_inputs.empty():
            msg = web_inputs.get()
            print(msg)
            if msg == 'skip':
                option = 'skip'
            elif msg == 'shuffle':
                playlist.shuff()
            else:
                print("unknown command")
                
        playlist.process()
        
        if isPlaying is False:
            if not playlist.empty():
                path = playlist.get_next()
                if path != '':
                    player = Player(path)
                    isPlaying = True
        if option == 'skip':
            player.stop()
            isPlaying = False
        else:
            time.sleep(0.1)

def start_web():
    app.run(host = '0.0.0.0', port=80, debug = False, threaded = True, use_reloader = False)
    
#create threads for other things
t = threading.Thread(target = player_update).start()
p = threading.Thread(target = start_web).start()