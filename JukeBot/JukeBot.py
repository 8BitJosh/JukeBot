from player import Player
from playlist import Playlist
from playlistList import PlaylistList
from config import Config

from aiohttp import web
import socketio
import asyncio

logs = []
shuffles = {}
skips = []

socketio = socketio.AsyncServer()
app = web.Application()
socketio.attach(app)

loop = asyncio.get_event_loop()

config = Config()
playlist = Playlist(config, socketio, loop)
player = Player(config, socketio, loop)
playlistlist = PlaylistList(config, socketio, loop)


def log(string):
    print(string, flush=True)
    logs.append(string)
    if len(logs) > config.logLength:
        del logs[0]


async def index(request):
    return web.FileResponse('./JukeBot/templates/index.html')


async def playlists(request):
    return web.FileResponse('./JukeBot/templates/playlists.html')


async def iprequest(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Client loaded page - {}".format(host), flush=True)
    return web.Response(text=str(host))


async def logrequest(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Person loaded the logs - {}".format(host), flush=True)

    loglist = 'Web user logs - \n'
    for entry in logs:
        loglist = loglist + '\n' + entry

    return web.Response(text=loglist)


@socketio.on('connected', namespace='/main')
async def connect(sid, ip):
    print('Client Connected - {} - {}'.format(sid, ip), flush=True)
    await sendAll()


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
    requester = message['ip']  # todo convert ip to device name

    if title != '':
        str = 'Queued Song - ' + title
        if '&' in title:
            str = str + '\nIf you wanted to add a playlist use the full playlist page that has "playlist" in the url'
            start_pos = title.find('&')
            msg = title[:start_pos]
        else:
            msg = title

        log('{} - Submitted - {}'.format(requester, title))
        p = loop.create_task(playlist.process(_title=msg, _requester=requester))
    else:
        str = 'Enter a Song Name'
    await socketio.emit('response', {'data': str}, namespace='/main', room=sid)


@socketio.on('button', namespace='/main')
async def button_handler(sid, msg):
    global playlist
    global player
    global skips
    global shuffles
    command = msg['data']

    if command == 'skip' and config.skippingEnable:
        if config.voteSkipNum is 0:
            await socketio.emit('response', {'data': 'Song Skipped'}, namespace='/main', room=sid)
            log('{} - Skipped song'.format(msg['ip']))
            await player.stop()
        else:
            if msg['ip'] not in skips:
                skips.append(msg['ip'])
                print("{} - Voted to skip the song".format(msg['ip']), flush=True)
            if len(skips) >= config.voteSkipNum:
                await socketio.emit('response', {'data': 'Song Skipped'}, namespace='/main', room=sid)
                log('Song was vote Skipped by {} people'.format(len(skips)))
                await player.stop()

    elif command == 'shuffle' and config.shuffleEnable:
        if config.shuffleLimit is 0:
            await socketio.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
            log('{} - Shuffled playlist'.format(msg['ip']))
            await playlist.shuff()
        else:
            if msg['ip'] in shuffles:
                shuffles[msg['ip']] = shuffles[msg['ip']] + 1
            else:
                shuffles[msg['ip']] = 1

            if shuffles[msg['ip']] <= config.shuffleLimit:
                await socketio.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
                log('{} - Shuffled playlist'.format(msg['ip']))
                await playlist.shuff()

    elif command == 'clear' and config.songDeletionEnable:
        await playlist.clearall()
        log('{} - Cleared all of playlist'.format(msg['ip']))
        await socketio.emit('response', {'data': 'Playlist Cleared'}, namespace='/main')

    elif command == 'pause':
        if player.isPaused():
            log('{} - Resumed the song'.format(msg['ip']))
            await socketio.emit('response', {'data': 'Song Resumed'}, namespace='/main')
            await socketio.emit('pause_button', {'data': 'Pause'}, namespace='/main', broadcast=True)
            await player.pause()
        elif player.running():
            log('{} - Paused the song'.format(msg['ip']))
            await socketio.emit('response', {'data': 'Song Paused'}, namespace='/main')
            await socketio.emit('pause_button', {'data': 'Resume'}, namespace='/main', broadcast=True)
            await player.pause()


@socketio.on('volume', namespace='/main')
async def set_volume(sid, msg):
    global player
    vol = int(msg['vol'])
    player.setVolume(vol)
    await socketio.emit('volume_set', {'vol': vol}, namespace='/main', broadcast = True)


@socketio.on('delete', namespace='/main')
async def delete_song(sid, msg):
    if config.songDeletionEnable:
        global playlist
        title = msg['title']
        index = msg['data']
        log('{} - Removed index {} title = {}'.format(msg['ip'], index, title))

        await playlist.remove(index, title)

        s = 'Removed song from playlist - ' + title
        await socketio.emit('response', {'data': s}, namespace='/main', room=sid)


@socketio.on('addPlaylist', namespace='/main')
async def aPlaylist(sid, msg):
    global playlist
    global playlistlist
    songs = playlistlist.getsongs(msg['title'])
    if songs == {}:
        return
    await socketio.emit('response', {'data': 'added playlist - ' + msg['title']}, namespace='/main', room=sid)
    await playlist.addPlaylist(songs, msg['ip'])


@socketio.on('savequeue', namespace='/main')
async def savequeue(sid, msg):
    if config.newPlaylists:
        global playlist
        global playlistlist
        await socketio.emit('response', {'data': 'Saving Current queue as playlist named - ' + str(msg['name'])}, namespace='/main', room=sid)
        print('{} - Saved queue as - {}'.format(msg['ip'], msg['name']), flush=True)

        songs = await playlist.getQueue()
        songs['data']['name'] = str(msg['name'])
        await playlistlist.addqueue(songs)


@socketio.on('newempty', namespace='/main')
async def newempty(sid, msg):
    if config.newPlaylists:
        global playlistlist
        await socketio.emit('response', {'data': 'Creating a new empty playlist named - ' + str(msg['name'])}, namespace='/main', room=sid)
        print('{} - Created a new playlist named - {}'.format(msg['ip'], msg['name']), flush=True)

        await playlistlist.newPlaylist(msg['name'])


@socketio.on('getplaylist', namespace='/main')
async def sendaplaylist(sid, msg):
    name = msg['data']
    print('user modifing - {}'.format(name))
    songs = playlistlist.getsongs(name)
    await socketio.emit('selectedplaylist', songs, namespace='/main', room=sid)


@socketio.on('add_song', namespace='/main')
async def addplaylistsong(sid, msg):
    if config.enablePlaylistEditing:
        await playlistlist.addSong(msg['playlistname'], msg['data'])
        print('{} - Added - {} - to - {}'.format(msg['ip'], msg['data'], msg['playlistname']), flush=True)

        songs = playlistlist.getsongs(msg['playlistname'])
        await socketio.emit('selectedplaylist', songs, namespace='/main', room=sid)


@socketio.on('removePlaySong', namespace='/main')
async def removeplaylistsong(sid, msg):
    if config.enablePlaylistEditing:
        await playlistlist.removeSong(msg['playlistname'], msg['index'], msg['title'])
        print('{} - Removed {} from playlist - {}'.format(msg['ip'], msg['title'], msg['playlistname']), flush=True)

        songs = playlistlist.getsongs(msg['playlistname'])
        await socketio.emit('selectedplaylist', songs, namespace='/main', room=sid)


@socketio.on('removePlaylist', namespace='/main')
async def removePlaylist(sid, msg):
    if config.enablePlaylistDeletion:
        if msg['title'].lower() == msg['userinput'].lower():
            await playlistlist.removePlaylist(msg['title'])
            print('{} - Removed playlist from server - {}'.format(msg['ip'], msg['title']), flush=True)
            await socketio.emit('selectedplaylist', {'data': {'name': 'Playlist:', 'dur':0}}, namespace='/main', room=sid)
        else:
            await socketio.emit('response', {'data': 'Incorrect name, Unable to remove playlist'}, namespace='/main', room=sid)


# Thread constantly looping to playsong / process the current command
async def player_update():
    global playlist
    global player
    global skips
    global shuffles

    while True:
        p = loop.create_task(playlist.download_next())

        if not player.running() and not player.isPaused():
            skips = []
            shuffles = {}
            if not (await playlist.empty()):
                song = await playlist.get_next()
                if song.dir != '':
                    await player.play(song)

        await asyncio.sleep(1)

loop.create_task(player_update())

app.router.add_get('/', index)
app.router.add_get('/playlists', playlists)
app.router.add_get('/ip', iprequest)
app.router.add_get('/log', logrequest)
app.router.add_static('/static/', path=str('./JukeBot/static'), name='static')
web.run_app(app, port=config.webPort)
