from skabenclient.config import DeviceConfig

# это словарь, в котором содержится минимальный конфиг, с которым может стартовать девайс
# сомнительное решение, надо бы это переписать потом.
#

ESSENTIAL = {
    'sound_files': {
             "default" : {
             "file": "default_noise.ogg",
             "remote": "url://",  # maybe join with loaded ...
             "loaded": True}
    },
    'phrase': {
        'content': [
            {'name':'default', 'repeat': 1}
        ],
        'repeat': -1
    },
    'play': False
}

class SoundConfig(DeviceConfig):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
