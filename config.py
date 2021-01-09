from skabenclient.config import DeviceConfigExtended


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


class SoundConfig(DeviceConfigExtended):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
