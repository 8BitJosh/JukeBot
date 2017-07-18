# JukeBot

Based on another project called MusicBot for discord ( https://github.com/Just-Some-Bots/MusicBot )
used to take music suggestions which are then searched for and played from youtube using youtube-dl

Song suggestions are added through a web interface

## Dependencys

use "pip install" to add these

youtube_dl
flask
wtforms

## What are its commands?

    '[songname]'            searches youtube for the songname and adds it to a play queue

    'playlist'              print out all the songs in the queue

    'shuffle'               shuffle the order of the song queue

    'skip'                  skip the current song and move to the next in the queue

## TODO

The skip and shuffle command will be moved to a seperate webpage for admin only
The playlist will be constantly on the webpage instead of having to be called atm it prints to console
