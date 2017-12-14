import json


def importConfig():
    with open('config.json') as file:
        config = json.load(file)

    # Main
    if type(config['main']['webPort']) != int:
        config['main']['webPort'] = defaults.webPort
        print('webport value needs to be an interger', flush=True)

    if type(config['main']['songcacheDir']) != str:
        config['main']['songcacheDir'] = defaults.songcacheDir
        print('cache dir needs to be a string', flush=True)
        # todo check if it is a valid url

    if type(config['main']['loglength']) != int:
        config['main']['loglength'] = defaults.loglength
        print('The length of the web log needs to be an interger', flush=True)

    # Player
    vol = config['player']['defaultVol']
    if (type(vol) != int) or (vol < 0) or (vol > 150):
        config['player']['defaultVol'] = defaults.defaultVol
        print('default needs to be an interger between 0-150', flush=True)

    # Playlist
    if config['playlist']['skippingEnable']:
        config['playlist']['skippingEnable'] = True
    elif not config['playlist']['skippingEnable']:
        config['playlist']['skippingEnable'] = False

    if config['playlist']['songDeletionEnable']:
        config['playlist']['songDeletionEnable'] = True
    elif not config['playlist']['songDeletionEnable']:
        config['playlist']['songDeletionEnable'] = False

    return config


class defaults:
    # Main
    webPort = 80
    songcacheDir = "cache"
    loglength = 30

    # player
    defaultVol = 100

    # playlist
    defaultSkipping = True
    defaultsongDeletionEnable = True
