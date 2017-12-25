from player import Player
from playlist import Playlist
from playlistList import PlaylistList
from process import Processor
from config import Config
from mainNamespace import mainNamespace

import socketio
import asyncio

from sanic import Sanic, response
from sanic_session import InMemorySessionInterface

logs = []

socketio = socketio.AsyncServer(async_mode='sanic', logger=False)
app = Sanic(__name__, log_config=None, configure_logging=False)

socketio.attach(app)

session_interface = InMemorySessionInterface(expiry=43200)

loop = asyncio.get_event_loop()

config = Config()

processor = Processor(config.songcacheDir, socketio, loop)

playlist = Playlist(config, socketio, loop, processor)
playlistlist = PlaylistList(config, socketio, loop, processor)
player = Player(config, socketio, loop)

main = mainNamespace(_playlist=playlist, _player=player, _playlistlist=playlistlist,
    _config=config, _loop=loop, _logs=logs, _namespace='/main')
socketio.register_namespace(main)


@app.middleware('request')
async def add_session_to_request(request):
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session_interface.save(request, response)


@app.route('/')
async def index(request):
    return await response.file('./JukeBot/templates/index.html')


@app.route('/playlists')
async def playlists(request):
    return await response.file('./JukeBot/templates/playlists.html')


@app.route('/ip')
async def iprequest(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Client loaded page - {}".format(host), flush=True)
    return response.text(str(host))


@app.route('/log')
async def logrequest(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Person loaded the logs - {}".format(host), flush=True)

    loglist = 'Web user logs - \n'
    for entry in logs:
        loglist = loglist + '\n' + entry

    return response.text(loglist)


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

app.static('/static', './JukeBot/static')
app.run(host='0.0.0.0', port=config.webPort, access_log=False)
