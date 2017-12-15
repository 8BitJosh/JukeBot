from player import Player
from playlist import Playlist
from playlistList import PlaylistList
from config import Config
from mainNamespace import mainNamespace

from aiohttp import web
import socketio
import asyncio

logs = []

socketio = socketio.AsyncServer()
app = web.Application()
socketio.attach(app)

loop = asyncio.get_event_loop()

config = Config()
playlist = Playlist(config, socketio, loop)
player = Player(config, socketio, loop)
playlistlist = PlaylistList(config, socketio, loop)

main = mainNamespace(_playlist=playlist, _player=player, _playlistlist=playlistlist,
    _config=config, _loop=loop, _logs=logs, _namespace='/main')
socketio.register_namespace(main)


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


async def player_update():
    global playlist
    global player
    global main

    while True:
        loop.create_task(playlist.download_next())

        if not player.running() and not player.isPaused():
            main.newSong()
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
