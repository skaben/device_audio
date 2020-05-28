from skabenclient.config import DeviceConfig

# это словарь, в котором содержится минимальный конфиг, с которым может стартовать девайс
# сомнительное решение, надо бы это переписать потом.

ESSENTIAL = {
        'sound_files': [
            {"name": "odin",
             "file": "1.wav",
             "repeat": "2",
             "current": False,  # set to false after repeat n times
             "remote": "url://",  # maybe join with loaded ...
             "loaded": True},
            {"name": "dwa",
             "file": "2.wav",
             "repeat": "-1",
             "current": True,  # played on repeat, current set False only when stopped
             "remote": "url://",
             "loaded": True},
            {"name": "tri",
             "file": "3.wav",
             "repeat": "1",
             "current": False,
             "remote": "url://",
             "loaded": False}
        ]
}

class SoundConfig(DeviceConfig):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
