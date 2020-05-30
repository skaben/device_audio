from skabenclient.config import DeviceConfig

# это словарь, в котором содержится минимальный конфиг, с которым может стартовать девайс
# сомнительное решение, надо бы это переписать потом.
#
ESSENTIAL = {
    'sound_files': {
             "odin" : {
             "file": "1.wav",
             "repeat": "2",
             "current": False,  # set to false after repeat n times
             "remote": "url://",  # maybe join with loaded ...
             "loaded": True},
            "dva": {
             "file": "2.wav",
             "repeat": "-1",
             "current": False,  # played on repeat, current set False only when stopped
             "remote": "url://",
             "loaded": True},
            "tri": {
             "file": "3.wav",
             "repeat": "1",
             "current": False,
             "remote": "http://localhost/3.wav",
             "loaded": True}
    },
    'uid': '',
    'play': False,
    'phrase': {
        'content': [
            {'name':'odin', 'repeat': 1},
            {'name':'dva', 'repeat': 1},
            {'name':'tri', 'repeat': 1}
        ],
        'repeat': 1
    }
}


class SoundConfig(DeviceConfig):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
