# ==================================================================================
#   File:   telemetryserver.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    This class reads in the IoTCentralPatterns from config.json and emits
#           a pub/sub model for a device to emulate values that map to the model
#           associated with the device.
#
#   Online:   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import json, sys, time, string, threading, asyncio, os, copy, datetime
import logging

# For dumping and Loading Address Space option
from pathlib import Path
from pubsub import pub

# our classes
from classes.config import Config
from classes.devicescache import DevicesCache
from classes.maptelemetry import MapTelemetry

class TelemetryServer():

    def __init__(self, Log):
      self.logger = Log

      # Instance maps
      self.telemetry_server_instance = None
      self.telemetry_server_instance_stop = None
      self.telemetry_server_instance_init = None

      # Logging Mappers
      data = [x for x in self.config["ClassLoggingMaps"] if x["Name"] == "TelemetryServer"]
      self.class_name_map = data[0]["LoggingId"]

      # Namespaces
      self.id_namespace_twins = None
      self.id_namespace_gateways = None
      self.id_namespace_devices = None

      # Load configuration
      self.config = []
      self.load_config()

      # Telemetry Mapping
      self.map_telemetry = []
      self.map_telemetry_interfaces = []
      self.map_telemetry_interfaces_variables = []

      # meta
      self.telemetry_interface = {}
      self.telemetry_payload = {}


    # -------------------------------------------------------------------------------
    #   Function:   run
    #   Usage:      The start function starts the OPC Server
    # -------------------------------------------------------------------------------
    async def run(self, TelemetryItem):

      for variable in TelemetryItem["Variables"]:
        self.logger.info("[TELEMETRY SERVER LOOP] VARIABLE (Display Name): %s" % variable["DisplayName"])
        self.logger.info("[TELEMETRY SERVER LOOP] VARIABLE (Telemetry Name): %s" % variable["TelemetryName"])

        # Update our iterator and boundaries
        if int(variable["RangeValueCurrent"]) < int(variable["RangeValueCount"]):
          variable["RangeValueCurrent"] = int(variable["RangeValueCurrent"]) + 1
        else:
          variable["RangeValueCurrent"] = 1

        value = variable["RangeValues"][int(variable["RangeValueCurrent"]) - 1]
        self.logger.info("[TELEMETRY SERVER LOOP] VARIABLE (Value) : %s" % value)
        self.telemetry_payload[variable["TelemetryName"]] = value

        self.telemetry_interface["Name"] = TelemetryItem["Name"]
        self.telemetry_interface["InterfacelId"] = TelemetryItem["InterfacelId"]
        self.telemetry_interface["InterfaceInstanceName"] = TelemetryItem["InterfaceInstanceName"]
        self.telemetry_interface["Payload"] = self.telemetry_payload

      pub.sendMessage("telemetry", result=self.telemetry_interface)
      self.telemetry_interface = {}
      self.telemetry_payload = {}

      return

      #except Exception as ex:
        #self.logger.error("[ERROR] %s" % ex)
        #self.logger.error("[TERMINATING] We encountered an error in TelemetryServer::run()" )

    # -------------------------------------------------------------------------------
    #   Function:   stop
    #   Usage:      The start function starts the OPC Server
    # -------------------------------------------------------------------------------
    async def stop(self):
      self.telemetry_server_instance_stop = None
      return

    # -------------------------------------------------------------------------------
    #   Function:   setup
    #   Usage:      The setup function preps the configuration for the OPC Server
    # -------------------------------------------------------------------------------
    async def setup(self):

      # Telemetry Server Setup
      try:

        for node in self.config["Nodes"]:
          self.logger.info("******* [TELEMETRY SETUP] ********")
          self.logger.info("INTERFACE: %s" % node["InterfacelId"])
          self.map_telemetry_interfaces = self.create_map_telemetry_root(node["Name"], node["InterfacelId"], node["InterfaceInstanceName"])

          for variable in node["Variables"]:
            self.map_telemetry_interfaces_variables.append(self.create_map_telemetry_variable(variable["DisplayName"], variable["TelemetryName"], variable["IoTCDataType"], variable["Frequency"], variable["OnlyOnValueChange"], variable["RangeValues"]))

          #self.logger.info("map_telemetry_interfaces_variables: %s" % self.map_telemetry_interfaces_variables)
          self.map_telemetry_interfaces["Variables"] = self.map_telemetry_interfaces_variables
          self.logger.info("map_telemetry_interfaces: %s" % self.map_telemetry_interfaces)
          self.map_telemetry_interfaces_variables = []
          self.map_telemetry.append(self.map_telemetry_interfaces)
          self.map_telemetry_interfaces = []

        self.logger.info("map_telemetry: %s" % self.map_telemetry)
        self.logger.info("****** [END TELEMETRY SETUP] *********")
        return

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in TelemetryServer Setup::setup()" )

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
    #   Function:   create_map_telemetry_root
    #   Usage:      Sets the root for the Map Telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_root(self, Name, InterfacelId, InterfaceInstanceName):
      mapTelemetry = {
        "Name": Name,
        "InterfacelId": InterfacelId,
        "InterfaceInstanceName": InterfaceInstanceName,
        "Created": str(datetime.datetime.now()),
        "Variables": [
        ]
      }
      return mapTelemetry


    # -------------------------------------------------------------------------------
    #   Function:   create_map_telemetry_variable
    #   Usage:      Sets the variable for the Map Telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_variable(self, DisplayName, TelemetryName, IoTCDataType, Frequency, OnlyOnValueChange, RangeValues):
      mapTelemetry = {
        "DisplayName": DisplayName,
        "TelemetryName": TelemetryName,
        "IoTCDataType": IoTCDataType,
        "Frequency": Frequency,
        "OnlyOnValueChange": OnlyOnValueChange,
        "RangeValueCount": len(RangeValues),
        "RangeValueCurrent": 1,
        "RangeValues": RangeValues
      }

      return mapTelemetry

    # -------------------------------------------------------------------------------
    #   Function:   get_map_telemetry
    #   Usage:      Returns the generated Map Telemetry File
    # -------------------------------------------------------------------------------
    def get_map_telemetry(self):
      return self.map_telemetry




