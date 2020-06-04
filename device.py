import os
import time
import json
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
        self.sound_path = os.path.join(system_config.root, 'resources', 'sound')
        self.phrase = self.config.get('phrase')
        self.snd_files = self.config.get('sound_files')
        try:
            if not os.path.exists(self.sound_path):
                self.logger.warning(f'Path for sound files {self.sound_path} not found. Creating...\n')
                os.makedirs(self.sound_path)
        except TypeError as exception_text:
            # а вот тут вполне себе сработает и трейсбек еще перехватит
            exc = f'cannot create directory for sound files\n{exception_text}'
            self.logger.exception(exc)
            raise Exception(exc)
        self.snd_check()
        self.snd_base_get()
        self.snd = self._snd_init(self.sound_path)

    def run(self):
        """ Main device run routine

            в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        while self.running:
            self.snd_base_get()
            phrase = self.config.get('phrase')
            phrase_new = phrase
            change_flag = False
            play_flag = self.config.get('play')
            if play_flag:
                if(phrase['repeat']>0):
                    range_iter = range(0,phrase['repeat'])
                else:
                    range_iter = cycle(range(0,len(phrase['content'])))
                try:
                    for i in range_iter:
                        for snd_name in phrase['content']:
                            for j in range(0,snd_name['repeat']):
                                snd_p = (self.snd_files[snd_name['name']]['file'].split('.'))[0]
                                self.snd.play(sound=snd_p, channel='fg')
                                while self.snd.channels['fg'].get_busy():
                                    phrase_new = self.config.get('phrase')
                                    play_flag = self.config.get('play')
                                    if (phrase_new != phrase or not play_flag):
                                        change_flag = True
                                        raise Exception('change play data')
                except:
                    pass
                if (change_flag):
                    phrase = phrase_new
                else:
                    play_flag = False
                self.state_update({'play': play_flag})
                time.sleep(0.2)

    def _snd_init(self, sound_dir):
        try:
            snd = SoundLoader(sound_dir=sound_dir)
        except Exception as e:
            self.logger.exception(f'failed to initialize sound module:\n{e}')
            snd = None
        return snd

    def snd_check(self):
        snd_files_tmp = {}
        for key, val in self.snd_files.items():
            snd_files_tmp[key] = val.copy()
            snd_full_name = os.path.join(self.sound_path, val['file'])
            snd_files_tmp[key]['loaded'] = os.path.isfile(snd_full_name)
        self.state_update({'sound_files': snd_files_tmp})

    def snd_get(self, snd_url, snd_file):
        try:
            print(snd_url)
            urllib.request.urlretrieve(snd_url, os.path.join(self.sound_path, snd_file))
        except Exception as e:
            self.logger.error(f'cannot retrieve {snd_url}:\n{e}')
            return (False)
        return (True)

    def snd_base_get(self):
        snd_files_tmp = {}
        for key, val in self.snd_files.items():
            snd_files_tmp[key] = val.copy()
            if not snd_files_tmp[key]['loaded']:
                snd_files_tmp[key]['loaded'] = self.snd_get(val.get('remote'), val.get('file'))
                if not snd_files_tmp[key]['loaded']:
                    del(snd_files_tmp[key])
        self.state_update({'sound_files': snd_files_tmp})

#    def snd_phrase_check(self):
#        snd_phrase_tmp = self.snd_files.copy()

