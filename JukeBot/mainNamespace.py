import socketio


class mainNamespace(socketio.AsyncNamespace):
    def __init__(self, _playlist, _player, _playlistlist, _config, _loop, _users, _namespace):
        self.playlist = _playlist
        self.player = _player
        self.playlistlist = _playlistlist
        self.config = _config
        self.loop = _loop
        self.users = _users

        self.shuffles = {}
        self.skips = []

        socketio.AsyncNamespace.__init__(self, namespace=_namespace)


    def newSong(self):
        self.shuffles = {}
        self.skips = []


    async def on_connected(self, sid, msg):
        self.users.userConnect(sid, msg['session'], msg['ip'])
        if self.users.isSidAdmin(sid):
            self.enter_room(sid, 'adminUsr', namespace='/main')
        else:
            self.enter_room(sid, 'stdUsr', namespace='/main')

        print('Client Connected - {} - {}'.format(sid, self.users.getSidName(sid)))
        await self.resendAll()


    async def on_sendAll(self, sid):
        await self.resendAll()


    async def resendAll(self):
        await self.emit('featureDisable', { 'skip': self.config.skippingEnable, 
                                            'delete': self.config.songDeletionEnable,
                                            'shuffle': self.config.shuffleEnable,
                                            'newplaylists': self.config.newPlaylists,
                                            'playlistdeletion': self.config.enablePlaylistDeletion,
                                            'playlistediting': self.config.enablePlaylistEditing },
                                            room='stdUsr')
        await self.emit('featureDisable', { 'skip': True, 'delete': True, 'shuffle': True, 'newplaylists': True, 'playlistdeletion': True, 
                                            'playlistediting': True},
                                            room='adminUsr')
        await self.playlist.sendPlaylist()
        await self.player.sendDuration()
        await self.emit('volume_set', {'vol': self.player.getVolume()})
        await self.emit('playlistList', self.playlistlist.getPlaylists())


    async def on_sent_song(self, sid, msg):
        global playlist
        title = msg['data']
        requester = self.users.getSidName(sid)  # todo convert ip to device name

        if title != '':
            str = 'Queued Song - ' + title
            if '&' in title:
                str = str + '\nIf you wanted to add a playlist use the full playlist page that has "playlist" in the url'
                start_pos = title.find('&')
                msg = title[:start_pos]
            else:
                msg = title

            print('{} - Submitted - {}'.format(requester, title))
            p = self.loop.create_task(self.playlist.process(_title=msg, _requester=requester))
        else:
            str = 'Enter a Song Name'
        await self.emit('response', {'data': str}, room=sid)


    async def on_button(self, sid, msg):
        command = msg['data']

        if command == 'skip' and (self.config.skippingEnable or self.users.isSidAdmin(sid)):
            if (self.config.voteSkipNum is 0) or self.users.isSidAdmin(sid):
                await self.emit('response', {'data': 'Song Skipped'}, room=sid)
                print('{} - Skipped song'.format(self.users.getSidName(sid)))
                await self.player.stop()
            else:
                if self.users.getSidName(sid) not in self.skips:
                    self.skips.append(self.users.getSidName(sid))
                    print("{} - Voted to skip the song".format(self.users.getSidName(sid)))
                if len(self.skips) >= self.config.voteSkipNum:
                    await self.emit('response', {'data': 'Song Skipped'}, room=sid)
                    print('Song was vote Skipped by {} people'.format(len(self.skips)))
                    await self.player.stop()

        elif command == 'shuffle' and (self.config.shuffleEnable or self.users.isSidAdmin(sid)):
            if (self.config.shuffleLimit is 0) or self.users.isSidAdmin(sid):
                await self.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
                print('{} - Shuffled playlist'.format(self.users.getSidName(sid)))
                await self.playlist.shuff()
            else:
                if self.users.getSidName(sid) in self.shuffles:
                    self.shuffles[self.users.getSidName(sid)] = self.shuffles[self.users.getSidName(sid)] + 1
                else:
                    self.shuffles[self.users.getSidName(sid)] = 1

                if self.shuffles[self.users.getSidName(sid)] <= self.config.shuffleLimit:
                    await self.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
                    print('{} - Shuffled playlist'.format(self.users.getSidName(sid)))
                    await self.playlist.shuff()

        elif command == 'clear' and (self.config.songDeletionEnable or self.users.isSidAdmin(sid)):
            await self.playlist.clearall()
            print('{} - Cleared all of playlist'.format(self.users.getSidName(sid)))
            await self.emit('response', {'data': 'Playlist Cleared'}, namespace='/main')

        elif command == 'pause':
            if self.player.isPaused():
                print('{} - Resumed the song'.format(self.users.getSidName(sid)))
                await self.emit('response', {'data': 'Song Resumed'}, namespace='/main')
                await self.emit('pause_button', {'data': 'Pause'})
                await self.player.pause()
            elif self.player.running():
                print('{} - Paused the song'.format(self.users.getSidName(sid)))
                await self.emit('response', {'data': 'Song Paused'}, namespace='/main')
                await self.emit('pause_button', {'data': 'Resume'})
                await self.player.pause()

  
    async def on_volume(self, sid, msg):
        vol = int(msg['vol'])
        self.player.setVolume(vol)
        await self.emit('volume_set', {'vol': vol})


    async def on_delete(self, sid, msg):
        if self.config.songDeletionEnable or self.users.isSidAdmin(sid):
            title = msg['title']
            index = msg['data']
            print('{} - Removed index {} title = {}'.format(self.users.getSidName(sid), index, title))

            await self.playlist.remove(index, title)

            s = 'Removed song from playlist - ' + title
            await self.emit('response', {'data': s}, room=sid)


    async def on_addPlaylist(self, sid, msg):
        songs = self.playlistlist.getsongs(msg['title'])
        if songs == {}:
            return
        await self.emit('response', {'data': 'added playlist - ' + msg['title']}, room=sid)
        await self.playlist.addPlaylist(songs, self.users.getSidName(sid))


    async def on_savequeue(self, sid, msg):
        if self.config.newPlaylists or self.users.isSidAdmin(sid):
            await self.emit('response', {'data': 'Saving Current queue as playlist named - ' + str(msg['name'])}, room=sid)
            print('{} - Saved queue as - {}'.format(self.users.getSidName(sid), msg['name']))

            songs = await self.playlist.getQueue()
            songs['data']['name'] = str(msg['name'])
            await self.playlistlist.addqueue(songs)


    async def on_newempty(self, sid, msg):
        if self.config.newPlaylists or self.users.isSidAdmin(sid):
            await self.emit('response', {'data': 'Creating a new empty playlist named - ' + str(msg['name'])}, room=sid)
            print('{} - Created a new playlist named - {}'.format(self.users.getSidName(sid), msg['name']))

            await self.playlistlist.newPlaylist(msg['name'])


    async def on_getplaylist(self, sid, msg):
        name = msg['data']
        print('user modifing - {}'.format(name))
        songs = self.playlistlist.getsongs(name)
        await self.emit('selectedplaylist', songs, room=sid)


    async def on_add_song(self, sid, msg):
        if self.config.enablePlaylistEditing or self.users.isSidAdmin(sid):
            await self.playlistlist.addSong(msg['playlistname'], msg['data'])
            print('{} - Added - {} - to - {}'.format(self.users.getSidName(sid), msg['data'], msg['playlistname']))

            songs = self.playlistlist.getsongs(msg['playlistname'])
            await self.emit('selectedplaylist', songs, room=sid)


    async def on_removePlaySong(self, sid, msg):
        if self.config.enablePlaylistEditing or self.users.isSidAdmin(sid):
            await self.playlistlist.removeSong(msg['playlistname'], msg['index'], msg['title'])
            print('{} - Removed {} from playlist - {}'.format(self.users.getSidName(sid), msg['title'], msg['playlistname']))

            songs = self.playlistlist.getsongs(msg['playlistname'])
            await self.emit('selectedplaylist', songs, room=sid)


    async def on_removePlaylist(self, sid, msg):
        if self.config.enablePlaylistDeletion or self.users.isSidAdmin(sid):
            if msg['title'].lower() == msg['userinput'].lower():
                await self.playlistlist.removePlaylist(msg['title'])
                print('{} - Removed playlist from server - {}'.format(self.users.getSidName(sid), msg['title']))
                await self.emit('selectedplaylist', {'data': {'name': 'Playlist:', 'dur':0}}, room=sid)
            else:
                await self.emit('response', {'data': 'Incorrect name, Unable to remove playlist'}, room=sid)
