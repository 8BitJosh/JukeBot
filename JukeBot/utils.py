import re
import unicodedata
import time
import traceback
import os


# reformat the titles so the titles are suitable for windows file names
def do_format(message):
    endMsg = unicodedata.normalize('NFKD', message).encode('ascii', 'ignore').decode('ascii')
    endMsg = re.sub('[^\w\s-]', '', endMsg).strip().lower()
    endMsg = re.sub('[-\s]+', '-', endMsg)
    return endMsg


def delete_file(dir):
    if dir == 'bad_path' or dir == '':
        print('No file exists - badpath/""')
        return
    for x in range(30):
        try:
            os.unlink(dir)
            print("file deleted - " + dir)
            break

        except PermissionError as e:
            if e.winerror == 32:  # File is in use
                time.sleep(0.25)

        except Exception as e:
            traceback.print_exc()
            print("Error trying to delete - " + dir)
            break
    else:
        print("Could not delete file {}, giving up and moving on".format(dir))


class PlaylistEntry:
    def __init__(self, url, title, duration=0):
        self.url = url
        self.title = title
        self.duration = duration
        self.downloaded = False
        self.dir = ''
