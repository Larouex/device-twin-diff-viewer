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
from classes.deviceclient import DeviceClient
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

      # Load configuration
      self.devicescache = []
      self.load_devicescache()

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

      # Device client list connected to Azure IoT Central/Hub
      self.device_client_dict = {}


    # -------------------------------------------------------------------------------
    #   Function:   run
    #   Usage:      The start function starts the Device Fleet
    # -------------------------------------------------------------------------------
    async def run(self, TelemetryServer):

      try:

        self.logger.info("[%s] Starting..." % self.class_name_map)

        # Subscribe to the Telemetry Server Publication of Telemetry Data
        pub.subscribe(self.listener, pub.ALL_TOPICS)

        print("HERE")
        print(self.devicescache)

        # Grab the Telemetry Enumeration (populated in TelemetryServer.setup())
        self.map_telemetry = TelemetryServer.get_map_telemetry()

        print("HERE2")
        print(self.map_telemetry)

        # Capture the index and list of connections
        index = 0

        # Create the device instances
        for device in self.devicescache["Devices"]:
          device_proxy = DeviceClient(self.logger, device["Device"]["Name"])
          self.logger.info("[%s] DEVICE %s" % (self.class_name_map, device_proxy))
          await device_proxy.connect()
          self.logger.info("[%s] CONNECTED %s" % (self.class_name_map, device_proxy))
          self.device_client_dict[device["Device"]["Name"]] = device_proxy
          #self.device_client.append(device_proxy)
          self.map_telemetry["Devices"][index]["Connected"] = True
          self.map_telemetry["Devices"][index]["ConnectedDateTime"] = str(datetime.datetime.now())
          index = index + 1

        while True:

          for telemetry in self.map_telemetry:
            self.logger.info("[%s LOOP] NAME: %s" % (self.class_name_map, telemetry["Name"]))
            self.logger.info("[%s LOOP] INTERFACE: %s" % (self.class_name_map, telemetry["InterfacelId"]))

            await TelemetryServer.run(telemetry)

            self.payload = self.listener.read_payload()
            map_telemetry_interfaces = TelemetryServer.create_map_telemetry_root(self.payload["Name"], self.payload["InterfacelId"], self.payload["InterfaceInstanceName"])
            map_telemetry_interfaces["Variables"] = self.payload["Payload"]
            self.logger.info("[%s LOOP] PUBLISHED: %s" % (self.class_name_map, map_telemetry_interfaces))

            # Enumerate the devices and send telemetry
            for device in self.map_telemetry["Devices"]:

              # hard wait for throttling, adjust as needed
              await asyncio.sleep(1)

              self.logger.info("[%s LOOP] SENDING PAYLOAD IOT CENTRAL" % self.class_name_map)
              self.logger.info("[%s LOOP] InterfacelId: %s" % (self.class_name_map, map_telemetry_interfaces["InterfacelId"]))
              self.logger.info("[%s LOOP] InterfaceInstanceName: %s" % (self.class_name_map, map_telemetry_interfaces["InterfaceInstanceName"]))

              device_proxy = self.device_client_dict[device["Name"]]
              await device_proxy.send_telemetry(map_telemetry_interfaces["Variables"], map_telemetry_interfaces["InterfacelId"], map_telemetry_interfaces["InterfaceInstanceName"])
              self.logger.info("[%s LOOP] PAYLOAD SENT SUCCESS" % self.class_name_map)


          self.logger.info("[%s LOOP] WAITING: %s" % (self.class_name_map, self.config["ServerFrequencyInSeconds"]))
          await asyncio.sleep(self.config["ServerFrequencyInSeconds"])

        return

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in the Run Loop for %s" % self.class_name_map)

      finally:

        index = 0
        for device in self.device_client_dict:
          device_proxy = self.device_client_dict[device["Name"]]
          await device_proxy.disconnect()
          self.logger.info("[%s] DISCONNECTING: %s" % (self.class_name_map, device))
          self.map_telemetry["Devices"][index]["Connected"] = False
          index = index + 1

        self.update_map_telemetry()

        return 0

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration from file
    # -------------------------------------------------------------------------------
    def load_config(self):

      config = Config(self.logger)
      self.config = config.data
      return

    # -------------------------------------------------------------------------------
    #   Function:   load_devicescache
    #   Usage:      Loads the Devices that have been registered and provisioned.
    #               This file is generated from the as-is state of the system
    #               when the TelemetryServer is started.
    # -------------------------------------------------------------------------------
    def load_devicescache(self):

      devicescache = DevicesCache(self.logger)
      self.devicescache = devicescache.data
      return

    # -------------------------------------------------------------------------------
    #   Function:   update_map_telemetry
    #   Usage:      Saves the generated Map Telemetry File
    # -------------------------------------------------------------------------------
    def update_map_telemetry(self):

      map_telemetry_file = MapTelemetry(self.logger)
      map_telemetry_file.update_file(self.map_telemetry)
      return
