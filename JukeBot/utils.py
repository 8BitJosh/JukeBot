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
        print('No file exists - badpath/""')
        return
    for x in range(30):
        try:
            os.unlink(dir)
            print("file deleted - {}".format(dir))
            break

        except PermissionError as e:
            if e.winerror == 32:  # File is in use
                asyncio.sleep(0.25)

        except Exception as e:
            traceback.print_exc()
            print("Error trying to delete - {}".format(dir))
            break
    else:
        print("Could not delete file {}, giving up and moving on".format(dir))


def tail(filename, linesback=10):
    avgcharsperline = 75

    file = open(filename, 'r')
    while 1:
        try:
            file.seek(-1 * avgcharsperline * linesback, 2)
        except IOError:
            file.seek(0)
        if file.tell() == 0:
            atstart = 1
        else:
            atstart = 0

        lines = file.read().split("\n")
        if (len(lines) > (linesback + 1)) or atstart:
            break

        avgcharsperline = avgcharsperline * 1.3
    file.close()

    if len(lines) > linesback:
        start = len(lines) - linesback - 1
    else:
        start = 0

    out = ''
    for l in lines[start:len(lines) - 1]:
        out = out + l + "\n"
    return out


class PlaylistEntry:
    def __init__(self, url, title, duration=0, requester=''):
        self.url = url
        self.title = title
        if type(duration) is int or type(duration) is float:
            self.duration = duration
        else:
            self.duration = 0            
        self.requester = requester
        self.downloaded = False
        self.downloading = False
        self.dir = ''
