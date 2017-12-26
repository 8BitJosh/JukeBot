import socketio
from utils import tail


class adminNamespace(socketio.AsyncNamespace):
    def __init__(self, _config, _authUsers, _loop, _namespace):
        self.config = _config
        self.loop = _loop
        self.authUsers = _authUsers

        self.shuffles = {}
        self.skips = []

        socketio.AsyncNamespace.__init__(self, namespace=_namespace)


    async def sendLog(self):
        await self.emit('logs', tail('CMDlog', self.config.logLength))


    async def on_connected(self, sid, cookie):
        if cookie in self.authUsers:
            await self.emit('currentConfig', self.config.getConfig())
            await self.sendLog()
        else:
            await self.emit('reloadpage')


    async def on_updateConfig(self, sid, data):
        if data['cookie'] in self.authUsers:
            print('Admin updated the server config', flush=True)

            self.config.updateConfig(data)
        else:
            print('Unautherized user tried to update the config', flush=True)

        await self.emit('currentConfig', self.config.getConfig())
