# ==================================================================================
#   File:   devicefleet.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Run a fleet of devices that are sending data from telemetryserver
#
#   Online:   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import json, sys, time, string, threading, asyncio, os, copy, datetime
import logging

# PubSub module
from pubsub import pub

# our classes
from classes.config import Config
from classes.devicescache import DevicesCache
from classes.maptelemetry import MapTelemetry

global Name
global InterfacelId
global InterfaceInstanceName
global Payload
class Listener:

    def __init__(self):
      self.payload = None

    def __call__(self, **kwargs):
      # read and parse the payload
      self.payload =  kwargs["result"]

    def read_payload(self):
      return self.payload

class DeviceFleet():

    def __init__(self, Log, WhatIf):
      self.logger = Log
      self.whatif = WhatIf

      # Load configuration
      self.config = []
      self.load_config()
      self.payload = {}

      self.listener = Listener()

    # -------------------------------------------------------------------------------
    #   Function:   run
    #   Usage:      The start function starts the Device Fleet
    # -------------------------------------------------------------------------------
    async def run(self, TelemetryServer):

      self.logger.info("[DEVICE FLEET] Starting Telemetry Server...")

      pub.subscribe(self.listener, pub.ALL_TOPICS)

      while True:

        await TelemetryServer.run()
        self.payload = self.listener.read_payload()
        map_telemetry_interfaces = TelemetryServer.create_map_telemetry_root(self.payload["Name"], self.payload["InterfacelId"], self.payload["InterfaceInstanceName"])
        map_telemetry_interfaces["Variables"] = self.payload["Payload"]
        self.logger.info("DeviceFleet: map_telemetry_interfaces: %s" % map_telemetry_interfaces)
        print("larouex larouex larouex")


      return

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration from file
    # -------------------------------------------------------------------------------
    def load_config(self):

      config = Config(self.logger)
      self.config = config.data
      return
