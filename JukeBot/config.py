import json


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
        self.voteSkipEnable = False     #
        self.voteSkipNum = 2            #

        self.songDeletionEnable = True
        self.shuffleEnable = True       
        self.shuffleLimit = 0           #

        # stored Playlists
        self.newPlaylists = True            #
        self.enablePlaylistDeletion = True  #
        self.enablePlaylistEditing = True   #

        self.importConfig()


    def importConfig(self):
        with open('config.json') as file:
            config = json.load(file)

        # Main
        if type(config['webPort']) is int:
            self.webPort = config['webPort']
        else:
            print('Webport value needs to be an interger', flush=True)
            print("Setting Webport to a default of {}".format(self.webPort))

        # TODO check if the dir is a valid path
        if type(config['songcacheDir']) is str:
            self.songcacheDir = config['songcacheDir']
        else:
            print('cache Dir needs to be a valid directory', flush=True)
            print("Setting cache Directory to a default of \"{}\"".format(self.songcacheDir))            

        if type(config['logLength']) is int:
            self.logLength = config['logLength']
        else:
            print('The length of the web log needs to be an interger', flush=True)
            print('Setting the log length to a default of {}'.format(self.logLength))

        # Player
        vol = config['defaultVol']
        if (type(vol) is int) and (vol >= 0) and (vol <= 150):
            self.defaultVol = config['defaultVol']
        else:
            print('Default volume needs to be an interger between 0-150', flush=True)
            print('Setting the volume to a default of {}'.format(self.defaultVol))

        # Playlist
        if config['skippingEnable']:
            self.skippingEnable = True
        elif not config['skippingEnable']:
            self.skippingEnable = False

        # need to do checking on this data to check user input
        self.skippingEnable = config['skippingEnable']
        self.voteSkipNum = config['voteSkipNum']

        if config['songDeletionEnable']:
            self.songDeletionEnable = True
        elif not config['songDeletionEnable']:
            self.songDeletionEnable = False

        if config['shuffleEnable']:
            self.shuffleEnable = True
        elif not config['shuffleEnable']:
            self.shuffleEnable = False

        # need to do checks on this data to check user input
        self.shuffleLimit = config['shuffleLimit']

        self.newPlaylists = config['newPlaylists']
        self.enablePlaylistDeletion = config['enablePlaylistDeletion']
        self.enablePlaylistEditing = config['enablePlaylistEditing']


    def exportConfig(self):
        with open('config.json', 'w') as file:
            json.dump(self.__dict__, file, indent="\t")


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