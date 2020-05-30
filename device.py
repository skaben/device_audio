import logging
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
        self.sound_path = system_config.get('sound_path')
        self.snd = self._snd_init(self.sound_path)
        self.phrase = self.config.get('phrase')
        self.play_flag = self.config.get('play')
        if not os.path.exists(self.sound_path):
            logging.exception(f'Path for sound files {self.sound_path} not found. Creating...\n')
            os.makedirs(self.sound_path)
        self.snd_files = self.config.get('sound_files')
        self.snd_check()
        for sndf in self.snd_files.keys():
            if not self.snd_files[sndf]['loaded']:
                self.snd_files[sndf]['loaded'] = self.snd_get(self.snd_files[sndf]['remote'],
                                                              self.snd_files[sndf]['file'])
        # print({'sound_files': self.snd_files})
        self.state_update({'uid': 'uid'})
        # self.state_update({'test':'test'})

    def run(self):
        """ Main device run routine

            в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        while self.running:
            if self.play_flag:
                i = 0
                if self.phrase['repeat'] < 0:
                    i = -128
                while i < self.phrase['repeat']:
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

    def snd_check(self):
        for snd in self.snd_files.keys():
            snd_full_name = os.path.join(self.sound_path,self.snd_files[snd]['file'])
            self.snd_files[snd]['loaded'] = os.path.isfile(snd_full_name)


    def snd_get(self,snd_url,snd_file):
        try:
            urllib.request.urlretrieve(snd_url, os.path.join(self.sound_path,snd_file))
        except:
            return (False)
        return (True)

    def _snd_init(self, sound_dir):
        try:
            snd = SoundLoader(sound_dir=sound_dir)
        except:
            logging.exception('failed to initialize sound module')
            snd = None
        return snd
