# JukeBot

Based on another project called MusicBot for discord ( https://github.com/Just-Some-Bots/MusicBot )
used to take music suggestions which are then searched for and played from youtube using youtube-dl

Song suggestions are added through a web interface, 
where the user can also see the playlist, shuffle the playlist or skip the current song

The song suggestions can be added via the song title which will be found through a YT search
or a direct link to the youtube song

## Dependencys

run update_dep to install dependencies or
use "pip install" to add these

youtube_dl
flask
wtforms

## TODO

- change the playlist class to allow the user to add songs by a playlist
- come up with a better player class, the current player is quite bodged limited in commands ( no pause/resume ) and 
the way some of the functions work
