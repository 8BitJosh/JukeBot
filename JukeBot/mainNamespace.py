import socketio


class mainNamespace(socketio.AsyncNamespace):
    def __init__(self, _playlist, _player, _playlistlist, _config, _loop, _logs, _namespace):
        self.playlist = _playlist
        self.player = _player
        self.playlistlist = _playlistlist
        self.config = _config
        self.loop = _loop
        self.logs = _logs

        self.shuffles = {}
        self.skips = []

        socketio.AsyncNamespace.__init__(self, namespace=_namespace)


    def log(self, string):
        print(string, flush=True)
        self.logs.append(string)
        if len(self.logs) > self.config.logLength:
            del self.logs[0]


    def newSong(self):
        self.shuffles = {}
        self.skips = []


    async def on_connected(self, sid, ip):
        print('Client Connected - {} - {}'.format(sid, ip), flush=True)
        await self.resendAll()


    async def on_sendAll(self, sid):
        await self.resendAll()


    async def resendAll(self):
        await self.emit('featureDisable', { 'skip': self.config.skippingEnable, 
                                            'delete': self.config.songDeletionEnable,
                                            'shuffle': self.config.shuffleEnable,
                                            'newplaylists': self.config.newPlaylists,
                                            'playlistdeletion': self.config.enablePlaylistDeletion,
                                            'playlistediting': self.config.enablePlaylistEditing })
        await self.playlist.sendPlaylist()
        await self.player.sendDuration()
        await self.emit('volume_set', {'vol': self.player.getVolume()})
        await self.emit('playlistList', self.playlistlist.getPlaylists())


    async def on_sent_song(self, sid, message):
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

            self.log('{} - Submitted - {}'.format(requester, title))
            p = self.loop.create_task(self.playlist.process(_title=msg, _requester=requester))
        else:
            str = 'Enter a Song Name'
        await self.emit('response', {'data': str}, room=sid)


    async def on_button(self, sid, msg):
        command = msg['data']

        if command == 'skip' and self.config.skippingEnable:
            if self.config.voteSkipNum is 0:
                await self.emit('response', {'data': 'Song Skipped'}, room=sid)
                self.log('{} - Skipped song'.format(msg['ip']))
                await self.player.stop()
            else:
                if msg['ip'] not in self.skips:
                    self.skips.append(msg['ip'])
                    print("{} - Voted to skip the song".format(msg['ip']), flush=True)
                if len(self.skips) >= self.config.voteSkipNum:
                    await self.emit('response', {'data': 'Song Skipped'}, room=sid)
                    self.log('Song was vote Skipped by {} people'.format(len(self.skips)))
                    await self.player.stop()

        elif command == 'shuffle' and self.config.shuffleEnable:
            if self.config.shuffleLimit is 0:
                await self.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
                self.log('{} - Shuffled playlist'.format(msg['ip']))
                await self.playlist.shuff()
            else:
                if msg['ip'] in self.shuffles:
                    self.shuffles[msg['ip']] = self.shuffles[msg['ip']] + 1
                else:
                    self.shuffles[msg['ip']] = 1

                if self.shuffles[msg['ip']] <= self.config.shuffleLimit:
                    await self.emit('response', {'data': 'Songs Shuffled'}, namespace='/main')
                    self.log('{} - Shuffled playlist'.format(msg['ip']))
                    await self.playlist.shuff()

        elif command == 'clear' and self.config.songDeletionEnable:
            await self.playlist.clearall()
            self.log('{} - Cleared all of playlist'.format(msg['ip']))
            await self.emit('response', {'data': 'Playlist Cleared'}, namespace='/main')

        elif command == 'pause':
            if self.player.isPaused():
                self.log('{} - Resumed the song'.format(msg['ip']))
                await self.emit('response', {'data': 'Song Resumed'}, namespace='/main')
                await self.emit('pause_button', {'data': 'Pause'})
                await self.player.pause()
            elif self.player.running():
                self.log('{} - Paused the song'.format(msg['ip']))
                await self.emit('response', {'data': 'Song Paused'}, namespace='/main')
                await self.emit('pause_button', {'data': 'Resume'})
                await self.player.pause()

  
    async def on_volume(self, sid, msg):
        vol = int(msg['vol'])
        self.player.setVolume(vol)
        await self.emit('volume_set', {'vol': vol})


    async def on_delete(self, sid, msg):
        if self.config.songDeletionEnable:
            title = msg['title']
            index = msg['data']
            self.log('{} - Removed index {} title = {}'.format(msg['ip'], index, title))

            await self.playlist.remove(index, title)

            s = 'Removed song from playlist - ' + title
            await self.emit('response', {'data': s}, room=sid)


    async def on_addPlaylist(self, sid, msg):
        songs = self.playlistlist.getsongs(msg['title'])
        if songs == {}:
            return
        await self.emit('response', {'data': 'added playlist - ' + msg['title']}, room=sid)
        await self.playlist.addPlaylist(songs, msg['ip'])


    async def on_savequeue(self, sid, msg):
        if self.config.newPlaylists:
            await self.emit('response', {'data': 'Saving Current queue as playlist named - ' + str(msg['name'])}, room=sid)
            print('{} - Saved queue as - {}'.format(msg['ip'], msg['name']), flush=True)

            songs = await self.playlist.getQueue()
            songs['data']['name'] = str(msg['name'])
            await self.playlistlist.addqueue(songs)


    async def on_newempty(self, sid, msg):
        if self.config.newPlaylists:
            await self.emit('response', {'data': 'Creating a new empty playlist named - ' + str(msg['name'])}, room=sid)
            print('{} - Created a new playlist named - {}'.format(msg['ip'], msg['name']), flush=True)

            await self.playlistlist.newPlaylist(msg['name'])


    async def on_getplaylist(self, sid, msg):
        name = msg['data']
        print('user modifing - {}'.format(name))
        songs = self.playlistlist.getsongs(name)
        await self.emit('selectedplaylist', songs, room=sid)


    async def on_add_song(self, sid, msg):
        if self.config.enablePlaylistEditing:
            await self.playlistlist.addSong(msg['playlistname'], msg['data'])
            print('{} - Added - {} - to - {}'.format(msg['ip'], msg['data'], msg['playlistname']), flush=True)

            songs = self.playlistlist.getsongs(msg['playlistname'])
            await self.emit('selectedplaylist', songs, room=sid)


    async def on_removePlaySong(self, sid, msg):
        if self.config.enablePlaylistEditing:
            await self.playlistlist.removeSong(msg['playlistname'], msg['index'], msg['title'])
            print('{} - Removed {} from playlist - {}'.format(msg['ip'], msg['title'], msg['playlistname']), flush=True)

            songs = self.playlistlist.getsongs(msg['playlistname'])
            await self.emit('selectedplaylist', songs, room=sid)


    async def on_removePlaylist(self, sid, msg):
        if self.config.enablePlaylistDeletion:
            if msg['title'].lower() == msg['userinput'].lower():
                await self.playlistlist.removePlaylist(msg['title'])
                print('{} - Removed playlist from server - {}'.format(msg['ip'], msg['title']), flush=True)
                await self.emit('selectedplaylist', {'data': {'name': 'Playlist:', 'dur':0}}, room=sid)
            else:
                await self.emit('response', {'data': 'Incorrect name, Unable to remove playlist'}, room=sid)
