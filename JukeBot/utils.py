import re
import unicodedata

#reformat the titles so the titles are suitable for windows file names
def do_format(message):
    endMsg = unicodedata.normalize('NFKD', message).encode('ascii', 'ignore').decode('ascii')
    endMsg = re.sub('[^\w\s-]', '', endMsg).strip().lower()
    endMsg = re.sub('[-\s]+', '-', endMsg)
    return endMsg
    
class PlaylistEntry:
    def __init__(self, url, title, duration=0):
        self.url = url
        self.title = title
        self.duration = duration
        self.downloaded = False
        self.dir = ''
