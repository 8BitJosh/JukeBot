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

    Entering a song title on the webpage and selecting submit will queue the song
    
    The other buttons skip, shuffle, playlist will perform there respective function

## TODO

-move the playlist to a class
-store the playlist title/duration/url in structs instead of redownloading each time more efficient for webpage
-predownload to stop the delay between the songs