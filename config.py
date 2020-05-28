from skabenclient.config import DeviceConfig

# это словарь, в котором содержится минимальный конфиг, с которым может стартовать девайс
# сомнительное решение, надо бы это переписать потом.

ESSENTIAL = {
    'test': 'device',
    'data': {'some': 'data'}
}

class TesterConfig(DeviceConfig):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
