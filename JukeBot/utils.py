import re
import unicodedata
import asyncio
from datetime import datetime, timedelta
import traceback
import os
import csv
import json


# reformat the titles so the titles are suitable for windows file names
def do_format(message):
    endMsg = unicodedata.normalize('NFKD', message).encode('ascii', 'ignore').decode('ascii')
    endMsg = re.sub('[^\w\s-]', '', endMsg).strip().lower()
    endMsg = re.sub('[-\s]+', '-', endMsg)
    return endMsg


async def logcsv(song):
    with open('SongLog.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("[%d/%m/%y %H:%M:%S]"), song.requester, song.title, timedelta(seconds=int(song.duration)), song.url]) 


def delete_file(dir):
    if dir == 'bad_path' or dir == '':
        print('No file exists - badpath/""', flush=True)
        return
    for x in range(30):
        try:
            os.unlink(dir)
            print("file deleted - " + dir, flush=True)
            break

        except PermissionError as e:
            if e.winerror == 32:  # File is in use
                asyncio.sleep(0.25)

        except Exception as e:
            traceback.print_exc()
            print("Error trying to delete - " + dir, flush=True)
            break
    else:
        print("Could not delete file {}, giving up and moving on".format(dir), flush=True)


class PlaylistEntry:
    def __init__(self, url, title, duration=0, requester=''):
        self.url = url
        self.title = title
        self.duration = duration
        self.requester = requester
        self.downloaded = False
        self.downloading = False
        self.dir = ''


def importConfig():
    with open('config.json') as file:
        config = json.load(file)

    # Main
    if type(config['main']['webPort']) != int:
        config['main']['webPort'] = defaults.webPort
        print('webport value needs to be an interger', flush=True)

    if type(config['main']['songcacheDir']) != str:
        config['main']['songcacheDir'] = defaults.songcacheDir
        print('cache dir needs to be a string', flush=True)
        # todo check if it is a valid url

    if type(config['main']['loglength']) != int:
        config['main']['loglength'] = defaults.loglength
        print('The length of the web log needs to be an interger', flush=True)

    # Player
    vol = config['player']['defaultVol']
    if (type(vol) != int) or (vol < 0) or (vol > 150):
        config['player']['defaultVol'] = defaults.defaultVol
        print('default needs to be an interger between 0-150', flush=True)

    # Playlist
    if config['playlist']['skippingEnable']:
        config['playlist']['skippingEnable'] = True
    elif not config['playlist']['skippingEnable']:
        config['playlist']['skippingEnable'] = False

    return config


class defaults:
    # Main
    webPort = 80
    songcacheDir = "cache"
    loglength = 30

    # player
    defaultVol = 100

    # playlist
    defaultSkipping = True
