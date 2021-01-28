# ==================================================================================
#   File:   devicefleetserver.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Run a fleet of devices that are sending data from TelemetryServer
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

class DeviceFleetServer():

    def __init__(self, Log):
      self.logger = Log

      # Load configuration
      self.config = []
      self.load_config()

      # Logging Mappers
      data = [x for x in self.config["ClassLoggingMaps"] if x["Name"] == "DeviceFleetServer"]
      self.class_name_map = data[0]["LoggingId"]

      # payload that is published
      self.payload = {}

      # Telemetry Mapping
      self.map_telemetry = []

      # Subscriber to all messages from
      # Telemetry Server Publication messages
      self.listener = Listener()

    # -------------------------------------------------------------------------------
    #   Function:   run
    #   Usage:      The start function starts the Device Fleet
    # -------------------------------------------------------------------------------
    async def run(self, TelemetryServer):

      self.logger.info("[%s] Starting..." % self.class_name_map)

      # Subscribe to the Telemetry Server Publication of Telemetry Data
      pub.subscribe(self.listener, pub.ALL_TOPICS)

      # Grab the Telemetry Enumeration (populated in TelemetryServer.setup())
      self.map_telemetry = TelemetryServer.get_map_telemetry()

      while True:

        for telemetry in self.map_telemetry:
          self.logger.info("[%s LOOP] NAME: %s" % (self.class_name_map, telemetry["Name"]))
          self.logger.info("[%s LOOP] INTERFACE: %s" % (self.class_name_map, telemetry["InterfacelId"]))

          await TelemetryServer.run(telemetry)

          self.payload = self.listener.read_payload()
          map_telemetry_interfaces = TelemetryServer.create_map_telemetry_root(self.payload["Name"], self.payload["InterfacelId"], self.payload["InterfaceInstanceName"])
          map_telemetry_interfaces["Variables"] = self.payload["Payload"]
          self.logger.info("[%s LOOP] PUBLISHED: %s" % (self.class_name_map, map_telemetry_interfaces))

        self.logger.info("[%s LOOP] WAITING: %s" % (self.class_name_map, self.config["ServerFrequencyInSeconds"]))
        await asyncio.sleep(self.config["ServerFrequencyInSeconds"])


      return

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration from file
    # -------------------------------------------------------------------------------
    def load_config(self):

      config = Config(self.logger)
      self.config = config.data
      return
