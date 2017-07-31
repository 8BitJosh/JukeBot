# JukeBot 1.0

Based on another project called MusicBot for discord ( https://github.com/Just-Some-Bots/MusicBot )
used to take music suggestions which are then searched for and played from youtube using youtube-dl

Song suggestions are added through a web interface, 
where the user can also see the playlist, shuffle the playlist or skip the current song

songs can be added through: 
- song title (will return the first result in a youtube search 
- youtube/soundcloud url 
- youtube playlist url (must be main playlist page with playlist in the url)

Other websites supported by youtube-dl may work through adding page urls but this is untested

tested and runs on a raspberry pi

## Dependencys

run update_dep to install dependencies or
use "pip install" to add these

-youtube_dl
-flask
-flask_socketio
-eventlet

avlib also needs to be installed on the system the bot is running on as the bot uses avplay to play the audio

## Runing the bot

- make sure python 3.5+ is installed
- make sure all the dependencies are installed
- go to the main bot folder and run /JukeBot/JukeBot.py ( this is going to be replaced with a script to start it)
- you can connect to the bot by typing the ip address of the computer running the bot into a web browser on another computer
- the interface is quite simple at the moment so should be easy enough to work out
- songs can be added through: song title, youtube/soundcloud url or youtube playlist url.
- other websites supported by youtube-dl may work through adding urls but this is untested

## Web Interface
- screenshot of the web interface

![jukebot webpage screenshot](https://s4.postimg.org/yvz8qebq5/jukebot.png)

## TODO

This project is still in development with more features to come

-add more buttons and control, pause, clear playlist, etc...
- come up with a better player class, the current player is quite bodged limited in commands ( no pause/resume ) and 
the way some of the functions work, could use mplayer ?
- add playlist page so users can create playlists that are stored on the server and can be queued up. need to work
out how to do this user interface wise
- add more cases to the process function to accept and handle all types of possible user input from more sources
- find a better way to exit without having to terminate the process
