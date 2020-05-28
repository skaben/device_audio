import os
import sys
import json

from skabenclient.config import SystemConfig
from skabenclient.helpers import get_mac
from skabenclient.main import start_app

from dotenv import load_dotenv

from device import BoilerplateDevice
from config import BoilerplateConfig

root = os.path.abspath(os.path.dirname(__file__))

sys_config_path = os.path.join(root, 'conf', 'system.yml')
dev_config_path = os.path.join(root, 'conf', 'device.yml')

log_path = os.path.join(root, 'local.log')


if __name__ == "__main__":
    #
    # DO NOT FORGET TO RUN ./pre-run.sh install BEFORE FIRST START
    #

    # setting system configuration and logger
    app_config = SystemConfig(sys_config_path, root=root)
    app_config.logger(file_path=log_path)
    # inject arguments into system configuration
    dev_config = BoilerplateDevice(dev_config_path)
    # instantiating device
    device = BoilerplateDevice(app_config, dev_config)
    # start application
    start_app(app_config=app_config,
              device=device)
