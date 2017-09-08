from player import Player
from playlist import Playlist
from playlistList import PlaylistList
from utils import importConfig

from aiohttp import web
import socketio
import asyncio

config = importConfig()

socketio = socketio.AsyncServer()
app = web.Application()
socketio.attach(app)

loop = asyncio.get_event_loop()

playlist = Playlist(config, socketio, loop)
player = Player(config, socketio, loop)
playlistlist = PlaylistList(config, socketio, loop)

connectedDevices = {}

async def index(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Client loaded page - " + str(host), flush=True)
    return web.FileResponse('./JukeBot/templates/index.html')


@socketio.on('connected', namespace='/main')
async def connect(sid):
    await sendAll()


@socketio.on('device', namespace='/main')
def add_device(sid, ip):
    print('Client Connected - ' + str(sid) + ' - ' + ip, flush=True)
    connectedDevices[sid] = {'ip' : ip}

@socketio.on('disconnect')
def disconnect(sid):
    print('disconnected - ' + str(sid) + ' - ' + connectedDevices[sid]['ip'])
    del connectedDevices[sid]


@socketio.on('sendAll', namespace='/main')
async def resendAll(sid):
    await sendAll()

    
async def sendAll():
    global playlist
    global player
    global playlistlist
    await playlist.sendPlaylist()
    await player.sendDuration()
    await socketio.emit('volume_set', {'vol': player.getVolume()}, namespace='/main', broadcast = True)
    await socketio.emit('playlistList', playlistlist.getPlaylists(), namespace='/main', broadcast = True)


@socketio.on('sent_song', namespace='/main')
async def song_received(sid, message):
    global playlist
    title = message['data']
    requester = connectedDevices[sid]['ip']  # todo convert ip to device name

    if title != '':
        str = 'Queued Song - ' + title
        if '&' in title:
            str = str + '\nIf you wanted to add a playlist use the full playlist page that has "playlist" in the url'
            start_pos = title.find('&')
            msg = title[:start_pos]
        else:
            msg = title

        print(connectedDevices[sid]['ip'] + ' - Submitted - ' + title, flush=True)
        p = loop.create_task(playlist.process(_title=msg, _requester=requester))
    else:
        str = 'Enter a Song Name'
    await socketio.emit('response', {'data': str}, namespace='/main', room=sid)


@socketio.on('button', namespace='/main')
async def button_handler(sid, msg):
    global playlist
    global player
    command = msg['data']

    if command == 'skip':
        await socketio.emit('response', {'data': 'Song Skipped'}, namespace='/main', room=sid)
        print(connectedDevices[sid]['ip'] + ' - Skipped song', flush=True)
        await player.stop()
    elif command == 'shuffle':
        await socketio.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
        print(connectedDevices[sid]['ip'] + ' - Shuffled playlist', flush=True)
        await playlist.shuff()
    elif command == 'clear':
        await playlist.clearall()
        print(connectedDevices[sid]['ip'] + ' - Cleared all of playlist', flush=True)
        await socketio.emit('response', {'data': 'Playlist Cleared'}, namespace='/main')
    elif command == 'pause':
        if player.isPaused():
            print(connectedDevices[sid]['ip'] + ' - Resumed the song', flush=True)
            await socketio.emit('response', {'data': 'Song Resumed'}, namespace='/main')
            await socketio.emit('pause_button', {'data': 'Pause'}, namespace='/main', broadcast=True)
            await player.pause()
        elif player.running():
            print(connectedDevices[sid]['ip'] + ' - Paused the song', flush=True)
            await socketio.emit('response', {'data': 'Song Paused'}, namespace='/main')
            await socketio.emit('pause_button', {'data': 'Resume'}, namespace='/main', broadcast=True)
            await player.pause()


@socketio.on('volume', namespace='/main')
async def set_volume(sid, msg):
    global player
    vol = int(msg['vol'])
    player.setVolume(vol)
    print(connectedDevices[sid]['ip'] + ' - Set volume to ' + str(vol), flush = True)
    await socketio.emit('volume_set', {'vol': vol}, namespace='/main', broadcast = True)


@socketio.on('delete', namespace='/main')
async def delete_song(sid, msg):
    global playlist
    title = msg['title']
    index = msg['data']
    print(connectedDevices[sid]['ip'] + ' - Removed index ' + str(index) + ' title = ' + title, flush=True)

    await playlist.remove(index, title)

    s = 'Removed song from playlist - ' + title
    await socketio.emit('response', {'data': s}, namespace='/main', room=sid)


@socketio.on('addPlaylist', namespace='/main')
async def aPlaylist(sid, msg):
    global playlist
    global playlistlist
    songs = playlistlist.getsongs(str(msg['index']), msg['title'])
    if songs == {}:
        return
    await socketio.emit('response', {'data': 'added playlist - ' + msg['title']}, namespace='/main', room=sid)
    await playlist.addPlaylist(songs, connectedDevices[sid]['ip'])


# Thread constantly looping to playsong / process the current command
async def player_update():
    global playlist
    global player

    while True:
        p = loop.create_task(playlist.download_next())

        if not player.running() and not player.isPaused():
            if not (await playlist.empty()):
                song = await playlist.get_next()
                if song.dir != '':
                    await player.play(song)

        await asyncio.sleep(1)

loop.create_task(player_update())

app.router.add_get('/', index)
app.router.add_static('/static/', path=str('./JukeBot/static'), name='static')
web.run_app(app, port=config['main']['webPort'])
