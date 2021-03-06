from player import Player
from playlist import Playlist
from playlistList import PlaylistList
from process import Processor
from config import Config
from users import Users
from mainNamespace import mainNamespace
from adminNamespace import adminNamespace

from aiohttp import web
import socketio
import asyncio
import time, os, base64, sys


socketio = socketio.AsyncServer()
app = web.Application()
socketio.attach(app)

loop = asyncio.get_event_loop()

config = Config()
users = Users()

processor = Processor(config.songcacheDir, socketio, loop, config)

playlist = Playlist(config, socketio, loop, processor)
playlistlist = PlaylistList(config, socketio, loop, processor)
player = Player(config, socketio, loop)

main = mainNamespace(playlist, player, playlistlist, config, loop, users, '/main')
admin = adminNamespace(config, users, loop, '/admin')

socketio.register_namespace(main)
socketio.register_namespace(admin)


async def index(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
    print("Client loaded page - {}".format(host))
    return web.FileResponse('./JukeBot/templates/index.html')


async def playlists(request):
    global config

    if config.enablePlaylistPage:
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            host, port = peername
        print("Client loaded playlists - {}".format(host))
        return web.FileResponse('./JukeBot/templates/playlists.html')
    return web.HTTPFound('/')

async def iprequest(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername

    response = web.Response(text=str(host))
    if 'Jukebot' not in request.cookies:
        randomSID = base64.b64encode(os.urandom(16)).decode('utf-8').strip('=') + str(int(time.time()))
        response.set_cookie('Jukebot', randomSID)
    return response


async def adminpage(request):
    global users

    if 'Jukebot' in request.cookies:
        user = request.cookies['Jukebot']
        if users.isAdmin(user):
            print('Admin loaded the admin page')
            return web.FileResponse('./JukeBot/templates/admin.html')
        else:
            return web.HTTPFound('/login')
    else:
        response = web.HTTPFound('/login')
        randomSID = base64.b64encode(os.urandom(16)).decode('utf-8').strip('=') + str(int(time.time()))
        response.set_cookie('Jukebot', randomSID)
        return response


async def login(request):
    return web.FileResponse('./JukeBot/templates/login.html')


async def post_login(request):
    global users

    data = await request.post()

    if users.userLogin(data['login'], request.cookies['Jukebot']):
        print('User just logged into admin page')
    else:
        print('User just entered incorrect password for admin login')
    return web.Response(text='reload')


async def change_login(request):
    global users

    data = await request.post()

    if users.updatePass(request.cookies['Jukebot'], data['oldPassword'], data['newPassword']):
        print('Admin Updated the admin password')
        return web.Response(text='Password successfully changed')
    else:
        print('Admin failed to update the admin password')
        return web.Response(text='Incorrect password entered')


async def player_update():
    global playlist
    global player
    global main
    global admin
    global users

    while True:
        sys.stdout.flush()
        await admin.sendLog()
        users.removeOld()

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
app.router.add_get('/admin', adminpage)
app.router.add_get('/login', login)
app.router.add_post('/postlogin', post_login)
app.router.add_post('/changelogin', change_login)

app.router.add_static('/static/', path=str('./JukeBot/static'), name='static')

web.run_app(app, port=config.webPort)
