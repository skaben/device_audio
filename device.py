import os
import time
from itertools import cycle
import urllib.request


from skabenclient.device import BaseDevice
from skabenclient.loaders import SoundLoader
from skabenclient.helpers import make_event
from config import SoundConfig


class SoundDevice(BaseDevice):

    """ Test device should be able to generate all kind of messages

        state_reload -> загрузить текущий конфиг из файла
        state_update(data) -> записать конфиг в файл (и послать на сервер)
        send_message(data) -> отправить сообщение от имени девайса во внутреннюю очередь
    """
    config_class = SoundConfig

    def __init__(self, system_config, device_config, **kwargs):
        super().__init__(system_config, device_config)
        self.running = None
        # создаем директорию сначала, вообще все константы вначале объявляем
        # я бы также попросил ее создавать вот тут, это стандарт для терминала и замка
        self.sound_path = os.path.join(system_config.root, 'resources', 'sound')
        self.phrase = self.config.get('phrase')
        self.snd_files = self.config.get('sound_files')
        try:
            """ 
               логирование доступно через self.logger
               советую почитать таки BaseDevice - станет чуть яснее, как с этим жить)
               по поводу self.logger.exception два замечания:
               
               2. self.logger.exception имеет смысл использовать после except, а тут его нет.
               пунктом 1 я возможно сам где-то грешу - если это так, то это неправильно.
            """
            if not os.path.exists(self.sound_path):
                self.logger.warning(f'Path for sound files {self.sound_path} not found. Creating...\n')
                os.makedirs(self.sound_path)
        except TypeError as exception_text:
            # а вот тут вполне себе сработает и трейсбек еще перехватит
            exc = f'cannot create directory for sound files\n{exception_text}'
            self.logger.exception(exc)
            raise Exception(exc)
        # потом уже логика. если нет созданной директории - лоадер плюнет исключением, т.к. неоткуда лоадить.
        self.snd = self._snd_init(self.sound_path)
        self.snd_check()
        for key, value in self.snd_files.items():
            # вот тут лучше пользоваться .get мне кажется
            # и итерироваться можно через items - гораздо короче выходит
            loaded = value.get('loaded')
            if not loaded:
                # тут я бы тоже использовал .get на случай если таких ключей нет
                loaded = self.snd_get(value.get('remote'), value.get('file'))

    def run(self):
        """ Main device run routine

            в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        # ну вот тут прям просится объект сиквенса нарисовать
        # как в терминале, собственно, объект окна)
        while self.running:
            phrase = self.config.get('phrase')
            phrase_new = phrase
            change_flag = False
            play_flag = self.config.get('play')
            if play_flag:
                if(phrase['repeat']>0):
                    range_iter = range(0,phrase['repeat'])
                else:
                    range_iter = cycle(range(0,len(phrase['content'])))
                for i in range_iter:
                    # print(i)
                    """
                        вложенные while - лучше так не делать.
                        почему: при брейке верхнего while - невозможно выйти из нижних и все виснет намертво.
                        в этом виде это можно запускать в отдельном процессе и делать ему kill как только self.running = False
                    """
                    # и снова, пожалуйста, snake_case - camelCase только в именах классов
                    for snd_name in phrase['content']:
                        for j in range(0,snd_name['repeat']):
                            snd_p = (self.snd_files[snd_name['name']]['file'].split('.'))[0]
                            self.snd.play(sound=snd_p, channel='fg')
                            while self.snd.channels['fg'].get_busy():
                                phrase_new = self.config.get('phrase')
                                play_flag = self.config.get('play')
                                if (phrase_new != phrase or not play_flag):
                                    change_flag = True
                                    break
                            if (change_flag):
                                break
                        if (change_flag):
                            break
                    if (change_flag):
                        break
                if (change_flag):
                    phrase = phrase_new
                else:
                    play_flag = False
                self.state_update({'play': play_flag})
                time.sleep(0.2)

    def snd_check(self):
        # то же самое - итерирумся через items
        for key, val in self.snd_files.items():
            # и ставим пробелы между аргументами
            snd_full_name = os.path.join(self.sound_path, val['file'])
            val['loaded'] = os.path.isfile(snd_full_name)

    def snd_get(self, snd_url, snd_file):
        try:
            urllib.request.urlretrieve(snd_url, os.path.join(self.sound_path, snd_file))  # и тут тоже)
        # пустые эксепшны лучше не оставлять. линтеры на это ругаются
        except Exception as e:
            self.logger.error(f'cannot retrieve {snd_url}:\n{e}')
            return (False)
        return (True)

    def _snd_init(self, sound_dir):
        try:
            snd = SoundLoader(sound_dir=sound_dir)
        except Exception as e:
            self.logger.exception(f'failed to initialize sound module:\n{e}')
            snd = None
        return snd
