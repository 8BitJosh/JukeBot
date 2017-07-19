# JukeBot

Based on another project called MusicBot for discord ( https://github.com/Just-Some-Bots/MusicBot )
used to take music suggestions which are then searched for and played from youtube using youtube-dl

Song suggestions are added through a web interface, where the user can also see the playlist, shuffle the 
playlist or skip the current song

## Dependencys

use "pip install" to add these

youtube_dl
flask
wtforms

## TODO

- come up with a better player class, the current player is quite bodged limited in commands ( no pause/resume ) and 
the way some of the functions work
-use jquery and AJAX to make the webpage update the playlist without having to update the page
