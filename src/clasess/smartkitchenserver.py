# ==================================================================================
#   File:   smartkitchenserver.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    This class emulates a smart kitchen "Twin" scenario for n+1 instances
#
#   Online: https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import json, sys, time, string, threading, asyncio, os, copy, datetime
import logging

# For dumping and Loading Address Space option
from pathlib import Path

# our classes
from Classes.config import Config
from Classes.devicescache import DevicesCache
from Classes.maptelemetry import MapTelemetry


class SmartKitchenServer():

    def __init__(self, Log):
      self.logger = Log
      self.opcua_server_instance = None

      # Namespaces
      self.opcua_id_namespace_twins = None
      self.opcua_id_namespace_gateways = None
      self.opcua_id_namespace_devices = None

      # Load configuration
      self.config = []
      self.load_config()

      # Load Device Mapping
      self.devicescache = []
      self.load_devicescache()

      self.node_instances = {}
      self.variable_instances = {}

      # Telemetry Mapping
      self.map_telemetry = []
      self.map_telemetry_devices = []
      self.map_telemetry_interfaces = []
      self.map_telemetry_interfaces_variables = []

      # meta
      self.application_uri = None
      self.namespace = None
      self.device_capability_model_id = None
      self.device_capability_model = []
      self.device_name_prefix = None
      self.ignore_interface_ids = []



    # -------------------------------------------------------------------------------
    #   Function:   run
    #   Usage:      The start function starts the OPC Server
    # -------------------------------------------------------------------------------
    async def run(self):

      # OPCUA Server Run
      try:

        print("[OPCUASERVER]: Starting the OPCUA Server")

        async with self.opcua_server_instance:
          while True:
            await asyncio.sleep(self.config["ServerFrequencyInSeconds"])
            self.logger.info("[SERVER LOOP] STARTING:")
            print("[OPCUASERVER]: SERVER LOOP Running the OPCUA Server")

            for device in self.map_telemetry["Devices"]:
              for interface in device["Interfaces"]:
                for variable in interface["Variables"]:

                  # Get the values from our ranges we are writing
                  value = variable["RangeValues"][int(variable["RangeValueCurrent"]) - 1]
                  self.logger.info("[SERVER LOOP] VALUE: %s" % value)

                  # Update our iterator and boundaries
                  if int(variable["RangeValueCurrent"]) < int(variable["RangeValueCount"]):
                    variable["RangeValueCurrent"] = int(variable["RangeValueCurrent"]) + 1
                  else:
                    variable["RangeValueCurrent"] = 1

                  self.logger.info("int(variable[RangeValueCurrent]) %s" % int(variable["RangeValueCurrent"]))
                  self.logger.info("int(variable[RangeValueCount]) %s" % int(variable["RangeValueCount"]))

                  variable_node_instance = self.opcua_server_instance.get_node(variable["NodeId"])
                  await variable_node_instance.write_value(value)

        return
      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in OpcUaServer::run()" )

    # -------------------------------------------------------------------------------
    #   Function:   stop
    #   Usage:      The start function starts the OPC Server
    # -------------------------------------------------------------------------------
    async def stop(self):
      await self.opcua_server_instance.stop()
      return

    # -------------------------------------------------------------------------------
    #   Function:   setup
    #   Usage:      The setup function preps the configuration for the OPC Server
    # -------------------------------------------------------------------------------
    async def setup(self):

      # OPCUA Server Setup
      try:

        print("[OPCUASERVER]: Setting up the OPCUA Server")

        # configure the endpoint
        opc_url = self.config["ServerUrlPattern"].format(ip = self.config["IPAddress"], port = self.config["Port"])

        # init the server
        self.opcua_server_instance = Server()
        await self.opcua_server_instance.init()

        self.opcua_server_instance.set_endpoint(opc_url)
        self.opcua_server_instance.set_server_name(self.config["ServerDiscoveryName"])
        await self.opcua_server_instance.set_application_uri(self.config["ApplicationUri"])

        self.logger.info("[SERVER CONFIG] ENDPOINT: %s" % opc_url)
        self.logger.info("[SERVER CONFIG] APPLICATION URI: %s" % self.config["ApplicationUri"])
        self.logger.info("[SERVER CONFIG] APPLICATION NAME: %s" % self.config["ServerDiscoveryName"])

        # Set NameSpace(s)
        for pattern in self.config["IoTCentralPatterns"]:
          if pattern["ModelType"] == "Twins":
            self.opcua_id_namespace_twins = await self.opcua_server_instance.register_namespace(pattern["NameSpace"])
          if pattern["ModelType"] == "Gateways":
            self.opcua_id_namespace_gateways = await self.opcua_server_instance.register_namespace(pattern["NameSpace"])
          if pattern["ModelType"] == "Devices":
            self.opcua_id_namespace_devices = await self.opcua_server_instance.register_namespace(pattern["NameSpace"])

        self.logger.info("[SERVER CONFIG] NAMESPACE TWINS: %s" % self.opcua_id_namespace_twins)
        self.logger.info("[SERVER CONFIG] NAMESPACE TWINS: %s" % self.opcua_id_namespace_gateways)
        self.logger.info("[SERVER CONFIG] NAMESPACE DEVICES: %s" % self.opcua_id_namespace_devices)

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in OPCUA Server Setup::setup()" )

      print("[OPCUASERVER]: Completed setting up the OPCUA Server")

      return

    # -------------------------------------------------------------------------------
    #   Function:   load_nodes_from_devicecache
    #   Usage:      The load_nodes_from_devicecache function enumerates the
    #               devicescache.json and creates a node for each kind of
    #               Iot Central Device. It looks at a Twin and registers all
    #               of the interfaces and for devices, registers the interface
    # -------------------------------------------------------------------------------
    async def load_nodes_from_devicecache(self):

      # OPCUA Server Setup
      try:

        # Setup root for map telemetry configuration file
        self.logger.info("[SERVER] INITIATED MAP TELEMETRY FILE: %s" % self.map_telemetry)
        self.map_telemetry = self.create_map_telemetry_root(self.config["NameSpace"])

        # Data Type Mappings (OPCUA Datatypes to IoT Central Datatypes)
        variant_type = VariantType(self.logger)

        device_count = 0
        for device in self.devicescache["Devices"]:

          self.logger.info("[SERVER] DEVICE TYPE: %s" % device["DeviceType"])
          self.logger.info("[SERVER] DEVICE NAME: %s" % device["Name"])

          # DEVICE PER NODE
          namespace_id = None

          if device["DeviceType"] == "Twins":
            namespace_id = self.opcua_id_namespace_twins
          elif device["DeviceType"] == "Gateways":
            namespace_id = self.opcua_id_namespace_devices
          elif device["DeviceType"] == "Devices":
            namespace_id = self.opcua_id_namespace_devices

          self.logger.info("[SERVER] DEVICE TYPE: %s" % device["DeviceType"])
          self.logger.info("[SERVER] DEVICE NAME: %s" % device["Name"])

          self.node_instances[device["Name"]] = await self.opcua_server_instance.nodes.objects.add_object(namespace_id, device["Name"])
          self.logger.info("[SERVER] NODE ID: %s" % self.node_instances[device["Name"]])

          # Add the device info to the map telemetry file
          self.map_telemetry_devices.append(self.create_map_telemetry_device(device["Name"], str(self.node_instances[device["Name"]]), device["DeviceType"], device["DeviceCapabilityModelId"]))
          self.logger.info("[SERVER] ADDED DEVICE TO MAP TELEMETRY FILE: %s" % self.map_telemetry_devices)

          interface_count = 0
          for interface in device["Interfaces"]:

            # Add the interface info to the map telemetry file
            self.map_telemetry_interfaces.append(self.create_map_telemetry_interface(interface["Name"], interface["InterfacelId"], interface["InterfaceInstanceName"]))
            self.logger.info("[SERVER] ADDED INTERFACE TO MAP TELEMETRY FILE: %s" % self.map_telemetry_interfaces)

            config_interface = [obj for obj in self.config["Nodes"] if obj["InterfaceInstanceName"]==interface["InterfaceInstanceName"]]

            for variable in config_interface[0]["Variables"]:
              variable_name = variable["DisplayName"]
              telemetry_name = variable["TelemetryName"]
              range_value = variable["RangeValues"][0]
              opc_variant_type = variant_type.map_variant_type(variable["IoTCDataType"])

              # Log Verbose Feedback
              log_msg = "[SERVER] SETUP VARIABLES: *DISPLAY NAME: {dn} TELEMETRY NAME: {tn} *RANGE VALUE: {rv} *IoTC TYPE: {it} *OPC VARIANT TYPE {ovt} *OPC DATA TYPE {odt}"
              self.logger.info(log_msg.format(dn = variable["DisplayName"], vn = variable["TelemetryName"], tn = variable["TelemetryName"], rv = variable["RangeValues"][0], it = variable["IoTCDataType"], ovt = opc_variant_type, odt = opc_variant_type))

              # Create Node Variable
              nodeObject = await self.node_instances[device["Name"]].add_variable(namespace_id, telemetry_name, range_value)
              await nodeObject.set_writable()
              self.variable_instances[telemetry_name] = nodeObject

              # Append the variables to the Interfaces collection for the map telemetry file
              self.map_telemetry_interfaces_variables.append(self.create_map_telemetry_variable(variable_name, str(self.variable_instances[telemetry_name]), telemetry_name, variable["IoTCDataType"], variable["Frequency"], variable["OnlyOnValueChange"], variable["RangeValues"]))
              self.logger.info("[SERVER] MAP TELEMETRY VARIABLES APPEND: %s" % self.map_telemetry_interfaces[interface_count])

            # Save the variables to the Map Telemetry [Interface] Collection
            self.map_telemetry_interfaces[interface_count]["Variables"] = self.map_telemetry_interfaces_variables
            self.logger.info("[SERVER] MAP TELEMETRY INTERFACES APPEND: %s" % self.map_telemetry_interfaces[interface_count])
            interface_count = interface_count + 1
            self.map_telemetry_interfaces_variables = []

          # Append the Interfaces to the Devices collection for the map telemetry file
          self.map_telemetry_devices[device_count]["Interfaces"] = self.map_telemetry_interfaces
          device_count = device_count + 1
          self.map_telemetry_interfaces = []

        # Append the Devices to the Root collection for the map telemetry file
        self.map_telemetry["Devices"] = self.map_telemetry_devices
        self.logger.info("[SERVER] MAP TELEMETRY: %s" % self.map_telemetry)
        self.update_map_telemetry()

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in OPCUA Server Setup::load_nodes_from_devicecache()")

      return

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
    #               when the OpcUaServer is started.
    # -------------------------------------------------------------------------------
    def load_devicescache(self):

      devicescache = DevicesCache(self.logger)
      self.devicescache = devicescache.data
      return

    # -------------------------------------------------------------------------------
    #   Function:   create_map_telemetry_root
    #   Usage:      Sets the root for the Map Telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_root(self, NameSpace):
      mapTelemetry = {
        "NameSpace": NameSpace,
        "Created": str(datetime.datetime.now()),
        "Devices": [
        ]
      }
      return mapTelemetry

    # -------------------------------------------------------------------------------
    #   Function:   create_map_telemetry_device
    #   Usage:      Adds a device to the map telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_device(self, Name, OpcUaNodeId, DeviceType, DeviceCapabilityModelId):
      mapTelemetry = {
        "Name": Name,
        "NodeId": OpcUaNodeId,
        "DeviceType": DeviceType,
        "DeviceCapabilityModelId": DeviceCapabilityModelId,
        "Interfaces": [
        ]
      }
      return mapTelemetry

    # -------------------------------------------------------------------------------
    #   Function:   create_map_telemetry_interface
    #   Usage:      Sets the node for the Map Telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_interface(self, Name, InterfacelId, InterfaceInstanceName):
      mapTelemetry = {
        "Name": Name,
        "InterfacelId": InterfacelId,
        "InterfaceInstanceName": InterfaceInstanceName,
        "Variables":[
        ]
      }
      return mapTelemetry

    # -------------------------------------------------------------------------------
    #   Function:   create_map_telemetry_variable
    #   Usage:      Sets the variable for the Map Telemetry configuration file
    # -------------------------------------------------------------------------------
    def create_map_telemetry_variable(self, DisplayName, OpcUaNodeId, TelemetryName, IoTCDataType, Frequency, OnlyOnValueChange, RangeValues):
      mapTelemetry = {
        "DisplayName": DisplayName,
        "NodeId": OpcUaNodeId,
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
    #   Function:   update_map_telemetry
    #   Usage:      Saves the generated Map Telemetry File
    # -------------------------------------------------------------------------------
    def update_map_telemetry(self):
      map_telemetry_file = MapTelemetry(self.logger)
      map_telemetry_file.update_file(self.map_telemetry)
      return

