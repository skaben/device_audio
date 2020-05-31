import os
import time
import json
import urllib.request
import threading as th

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
        self.play_flag = self.config.get('play')
        self.snd_files = self.config.get('sound_files')
        try:
            """ 
               логирование доступно через self.logger
               советую почитать таки BaseDevice - станет чуть яснее, как с этим жить)
               по поводу self.logger.exception два замечания:
               1. на ошибки, которые восстанавливаются самим приложением лучше генерить error или warning
               2. self.logger.exception имеет смысл использовать после except, а тут его нет.
               пунктом 1 я возможно сам где-то грешу - если это так, то это неправильно.
            """
            if not os.path.exists(self.sound_path):
                self.logger.error(f'Path for sound files {self.sound_path} not found. Creating...\n')  
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
            if self.play_flag:
                i = 0
                if self.phrase['repeat'] < 0:
                    i = -128
                while i < self.phrase['repeat']:
                    """
                        вложенные while - лучше так не делать.
                        почему: при брейке верхнего while - невозможно выйти из нижних и все виснет намертво.
                        в этом виде это можно запускать в отдельном процессе и делать ему kill как только self.running = False
                    """
                    # и снова, пожалуйста, snake_case - camelCase только в именах классов
                    for sndName in self.phrase['content']:
                        j = 0
                        while j < sndName['repeat']:
                            snd_p = (self.snd_files[sndName['name']]['file'].split('.'))[0]
                            self.snd.play(sound=snd_p, channel='fg')
                            while self.snd.channels['fg'].get_busy():
                                time.sleep(0.1)
                            j = j + 1
                    if self.phrase['repeat'] > 0:
                        i += 1
                self.play_flag = False
                self.state_update({'play': self.play_flag})
                """
                скорее что-то такое:

                for i in range(0, self.phrase.get("repeat", 0) + 1):
                    for sound_name in self.phrase.get("content", []):
                        for counter in range(0, sound_name.get("repeat", 0) + 1):
                            sound = (self.snd_files[sound_name["name"]]["file"].split("."))[0]
                            self.snd.play(sound=sound, channel="fg")
                            while self.snd.channels["fg"].get_busy():
                                time.sleep(0.1)
                                if not self.running:
                                    raise SystemExit('exiting')
                """

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
