# ==================================================================================
#   File:   devices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Configuration File Management for devices.json
#
#   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import json
import logging

class Devices():

    def __init__(self, Log):
        self.logger = Log
        self.load_file()

    def load_file(self):
        with open('devices.json') as config_file:
            self.data = json.load(config_file)
            alerts = self.load_alerts()
            self.logger.debug(alerts["Alerts"]["Devices"]["Loaded"].format(self.data))

    def update_file(self, data):
        with open('devices.json', 'w') as configs_file:
            alerts = self.load_alerts()
            self.logger.debug(alerts["Alerts"]["Devices"]["Updated"].format(self.data))
            configs_file.write(json.dumps(data, indent=2))

    def load_alerts(self):
        with open('alerts.json', 'r') as alerts_file:
            return json.load(alerts_file)