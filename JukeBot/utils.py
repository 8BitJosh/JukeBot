import re
import unicodedata
import asyncio
from datetime import datetime, timedelta
import traceback
import os
import csv


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
