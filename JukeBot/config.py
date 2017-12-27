import json
import pprint

class Config:
    def __init__(self):
        # Defaults for values
        # main
        self.webPort = 80
        self.songcacheDir = "cache"
        self.logLength = 30

        # player
        self.defaultVol = 100

        # playlist
        self.skippingEnable = True
        self.voteSkipNum = 0

        self.songDeletionEnable = True
        self.shuffleEnable = True       
        self.shuffleLimit = 0

        self.maxPlaylistLength = 100

        # stored Playlists
        self.newPlaylists = True
        self.enablePlaylistDeletion = True
        self.enablePlaylistEditing = True
        self.enablePlaylistPage = True

        with open('config.json') as file:
            configfile = json.load(file)

        self.updateBootConfig(configfile['bootConfig'])
        self.updateConfig(configfile['liveConfig'])


    def updateConfig(self, config):

            # Playlist
        if 'skippingEnable' in config:
            if config['skippingEnable']:
                self.skippingEnable = True
            elif not config['skippingEnable']:
                self.skippingEnable = False

            # need to do checking on this data to check user input
        if 'voteSkipNum' in config:
            self.voteSkipNum = int(config['voteSkipNum'])

        if 'songDeletionEnable' in config:
            if config['songDeletionEnable']:
                self.songDeletionEnable = True
            elif not config['songDeletionEnable']:
                self.songDeletionEnable = False

        if 'shuffleEnable' in config:
            if config['shuffleEnable']:
                self.shuffleEnable = True
            elif not config['shuffleEnable']:
                self.shuffleEnable = False

            # need to do checks on this data to check user input
        if 'shuffleLimit' in config:
            self.shuffleLimit = int(config['shuffleLimit'])

        if 'maxPlaylistLength' in config:
            self.maxPlaylistLength = int(config['maxPlaylistLength'])

        if 'newPlaylists' in config:
            self.newPlaylists = config['newPlaylists']
            
        if 'enablePlaylistDeletion' in config:
            self.enablePlaylistDeletion = config['enablePlaylistDeletion']
            
        if 'enablePlaylistEditing' in config:
            self.enablePlaylistEditing = config['enablePlaylistEditing']

        if 'enablePlaylistPage' in config:
            self.enablePlaylistPage = config['enablePlaylistPage']

        self.exportConfig()
      
        print('Config-')
        self.printConfig(self.getConfig())


    def updateBootConfig(self, config):
        if 'webPort' in config:
            if type(config['webPort']) is int:
                self.webPort = config['webPort']
            else:
                print('Webport value needs to be an interger', flush=True)
                print("Setting Webport to a default of {}".format(self.webPort))

        # TODO check if the dir is a valid path
        if 'songcacheDir' in config:
            if type(config['songcacheDir']) is str:
                self.songcacheDir = config['songcacheDir']
            else:
                print('cache Dir needs to be a valid directory', flush=True)
                print("Setting cache Directory to a default of \"{}\"".format(self.songcacheDir))            

        if 'logLength' in config:
            if type(config['logLength']) is int:
                self.logLength = config['logLength']
            else:
                print('The length of the web log needs to be an interger', flush=True)
                print('Setting the log length to a default of {}'.format(self.logLength))

            # Player
        if 'defaultVol' in config:
            vol = config['defaultVol']
            if (type(vol) is int) and (vol >= 0) and (vol <= 150):
                self.defaultVol = config['defaultVol']
            else:
                print('Default volume needs to be an interger between 0-150', flush=True)
                print('Setting the volume to a default of {}'.format(self.defaultVol))

        self.exportConfig()
      
        print('Boot Config-')
        self.printConfig(self.getBootConfig())


    def exportConfig(self):
        with open('config.json', 'r') as file:
            Tosave = json.load(file)
        
        Tosave['liveConfig'] = self.getConfig()
        Tosave['bootConfig'] = self.getBootConfig()

        with open('config.json', 'w') as file:
            json.dump(Tosave, file, indent="\t")


    def getConfig(self):
        values = dict(self.__dict__)
        del values['webPort']
        del values['songcacheDir']
        del values['logLength']
        del values['defaultVol']
        return values


    def getBootConfig(self):
        values = {
            'webPort': self.webPort,
            'songcacheDir': self.songcacheDir,
            'logLength': self.logLength,
            'defaultVol': self.defaultVol
        }
        return values


    def printConfig(self, config):
        for key in list(config):
            print('\t{} = {}'.format(key, config[key]))


class defaults: 
    # Main 
    webPort = 80 
    songcacheDir = "cache" 
    logLength = 30 
 
    # player 
    defaultVol = 100 
 
    # playlist 
    defaultSkipping = True 
    defaultsongDeletionEnable = True 