# JukeBot 1.0

Based on another project called MusicBot for discord ( https://github.com/Just-Some-Bots/MusicBot )
used to take music suggestions which are then searched for and played from youtube using youtube-dl

Song suggestions are added through a web interface, 
where the user can also see the playlist, shuffle the playlist or skip the current song

songs can be added through: 
- song title (will return the first result in a youtube search 
- youtube/soundcloud/bandcamp url  (basicly any webpage supported by youtube-dl) 
- youtube playlist url (must be main playlist page with playlist in the url)

Other websites supported by youtube-dl may work through adding page urls but this is untested

## Web Interface
- screenshot of the web interface

![jukebot webpage screenshot](https://s27.postimg.org/wiv44hetv/Juke_Bot.png)

## Using this bot

The bot is still under development and has been running successfully on a raspberry pi 3

Below is a guide on how to setup the bot on the pi 3 with a fresh raspbian install

## Dependencies

Install git, vlc and python3-pip
``` 
sudo apt-get update
sudo apt-get install git vlc python3-pip
```

Reboot the pi
```
sudo reboot
```

Clone the repository and move inside the directory
```
git clone https://github.com/8BitJosh/JukeBot.git
cd ./JukeBot
```

Install the python dependencies 
```
sudo python3 -m pip install -U -r ./requirements.txt
```
This command installs the following python modules

- youtube_dl
- flask
- flask_socketio
- eventlet
- python-vlc

## Running the bot

To run the bot use the JukeBot script
```
./JukeBot.sh -h
```
Append this command with the letter corresponding to the function you want to perform
```
	-h  Display this help message.
	-f  Open JukeBot in a foreground process and tee output to CMDlog
	-b  Open JukeBot in a background process and redirect output to CMDlog
	-c  View the output log (implicit if no options specified)
	-e  End JukeBot running in a background process
	-l  List running bots
```
For example to start the bot as a background process run the command
```
./JukeBot.sh -b
```

## Connecting to the bot
- you can connect to the bot by typing the ip address of the computer running the bot into a web browser on another computer on the same network
- the interface is quite simple at the moment so should be easy enough to work out
- songs can be added through: song title, youtube/soundcloud url or youtube playlist url.

## TODO

This project is still in development with more features to come
