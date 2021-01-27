
# ==================================================================================
#   File:   provisiondevices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Provisions Devices and updates cache file and do device provisioning
#           via DPS for IoT Central
#
#   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import time, logging, string, json, os, binascii, struct, threading, asyncio, datetime

# Sur classes
from classes.devicescache import DevicesCache
from classes.secrets import Secrets
from classes.symmetrickey import SymmetricKey
from classes.config import Config

# uses the Azure IoT Device SDK for Python (Native Python libraries)
from azure.iot.device.aio import ProvisioningDeviceClient

# -------------------------------------------------------------------------------
#   ProvisionDevice Class
# -------------------------------------------------------------------------------
class ProvisionDevices():

    timer = None
    timer_ran = False
    dcm_value = None

    def __init__(self, Log, Id):

      self.logger = Log
      self.id_device = Id

      # Load the configuration file
      self.config = Config(self.logger)
      self.config = self.config.data

      # Symmetric Key
      self.symmetrickey = SymmetricKey(self.logger)

      # Secrets
      self.secrets = Secrets(self.logger)
      self.secrets_cache_data = self.secrets.data

      # meta
      self.application_uri = None
      self.namespace = None
      self.device_name = None
      self.device_default_component_id = None
      self.device_capability_model = []
      self.device_name_prefix = None
      self.ignore_interface_ids = []

      # Devices Cache
      self.devices_cache = DevicesCache(self.logger)
      self.devices_cache_data = self.devices_cache.data
      self.device_to_provision = None
      self.device_to_provision_array = []


    # -------------------------------------------------------------------------------
    #   Function:   provision_devices
    #   Usage:      Grabs the Defined Devices and Provisions into IoT Central
    #               a provisioning call to associated a device template to the node
    #               interface based on the twin, device or gateway pattern
    # -------------------------------------------------------------------------------
    async def provision_devices(self):

      # First up we gather all of the needed provisioning meta-data and secrets
      try:

        self.namespace = self.config["Device"]["NameSpace"]
        self.device_default_component_id = self.config["Device"]["DefaultComponentId"]
        self.device_name_prefix = self.config["Device"]["DeviceNamePrefix"]

        # this is our working cache for things we provision in this session
        self.device_to_provision = self.create_device_to_provision()
        self.device_create()

        print("************************************************")
        print("DEVICE TO PROVISION: %s" % self.device_to_provision)
        print("************************************************")

        # Azure IoT Central SDK Call to create the provisioning_device_client
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
          provisioning_host = self.secrets.get_provisioning_host(),
          registration_id = self.device_to_provision["Device"]["Name"],
          id_scope = self.secrets.get_scope_id(),
          symmetric_key = self.device_to_provision["Device"]["Secrets"]["DeviceSymmetricKey"],
          websockets=True
        )

        # Azure IoT Central SDK call to set the DCM payload and provision the device
        provisioning_device_client.provisioning_payload = '{"iotcModelId":"%s"}' % (self.device_to_provision["Device"]["DefaultComponentId"])
        registration_result = await provisioning_device_client.register()
        self.logger.info("[REGISTRATION RESULT] %s" % registration_result)
        self.logger.info("[DEVICE SYMMETRIC KEY] %s" % self.device_to_provision["Device"]["Secrets"]["DeviceSymmetricKey"])
        self.device_to_provision["Device"]["Secrets"]["AssignedHub"] = registration_result.registration_state.assigned_hub

        # Add Capabilities
        for node in self.config["Nodes"]:
          self.device_to_provision["Device"]["Capabilities"].append(node["InterfaceInstanceName"])

        # Now create/update our devices cache
        secrets_found_device = False
        devices_found_device = False

        if len(self.devices_cache_data["Devices"]) > 0:

          index = 0
          # Update Secrets Cache Data for Devices
          for device in self.secrets_cache_data["Devices"]:
            if device["Device"]["Name"] == self.device_to_provision["Device"]["Name"]:
              self.secrets_cache_data["Devices"][index] = self.device_to_provision
              secrets_found_device = True
              break
            else:
              index = index + 1

          index = 0
          # if we fell thru, add it
          if secrets_found_device == False:
            self.secrets_cache_data["Devices"].append(self.device_to_provision)

          for device in self.devices_cache_data["Devices"]:
            if device["Device"]["Name"] == self.device_to_provision["Device"]["Name"]:
              self.devices_cache_data["Devices"][index] = self.device_to_provision
              devices_found_device = True
              break
            else:
              index = index + 1

          # if we fell thru, add it
          if devices_found_device == False:
            self.devices_cache_data["Devices"].append(self.device_to_provision)

        # Update Full Device Information to the Secrets file.
        # IMPORTANT: This hides the secrets in file in .gitignore
        self.secrets.update_file_device_secrets(self.secrets_cache_data["Devices"])

        # Save to the Device Cache and null the secrets
        index = 0
        for device in self.devices_cache_data["Devices"]:
          self.devices_cache_data["Devices"][index]["Device"]["Secrets"] = None
          index = index + 1

        self.devices_cache.update_file(self.devices_cache_data)

        print("************************************************")
        print("DEVICE SUCCESSFULLY PROVISIONED: %s" % self.device_to_provision)
        print("************************************************")

        return

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in provision_devices()" )

    # -------------------------------------------------------------------------------
    #   Function:   device_create
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def device_create(self):

      try:

        self.device_name = self.device_name_prefix.format(id=self.id_device)
        self.device_default_component_id = self.config["Device"]["DefaultComponentId"]
        self.device_to_provision["Device"] = self.create_device_capability_model()
        self.device_to_provision["Device"]["Secrets"] = self.create_device_connection()
        self.logger.error("[PROVISION DEVICES] Device to Provision %s" % self.device_to_provision)

        return

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in devices_create()" )

    # -------------------------------------------------------------------------------
    #   Function:   create_device_to_provision`
    #   Usage:      Returns a Devices Array
    # -------------------------------------------------------------------------------
    def create_device_to_provision(self):
      newDeviceToProvision = {
        "Device": {
          "Secrets": {
          }
        }
      }
      return newDeviceToProvision

    # -------------------------------------------------------------------------------
    #   Function:   create_device_capability_model
    #   Usage:      Returns a Device Interface with the  Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_capability_model(self):
      newDeviceCapabilityModel = {
        "Name": self.device_name,
        "DefaultComponentId": self.device_default_component_id,
        "Capabilities": [
        ],
        "LastProvisioned": str(datetime.datetime.now())
      }
      return newDeviceCapabilityModel

    # -------------------------------------------------------------------------------
    #   Function:   create_device_interface
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_interface(self, name, Id, instantName):
      newInterface = {
        "Name": name,
        "InterfacelId": Id,
        "InterfaceInstanceName": instantName
      }
      return newInterface

    # -------------------------------------------------------------------------------
    #   Function:   create_device_connection
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_connection(self):

      # Get device symmetric key
      device_symmetric_key = self.symmetrickey.compute_derived_symmetric_key(self.device_name, self.secrets.get_device_secondary_key())

      newDeviceSecret = {
        "Name": self.device_name,
        "DefaultComponentId": self.device_default_component_id,
        "AssignedHub": "",
        "DeviceSymmetricKey": device_symmetric_key,
        "LastProvisioned": str(datetime.datetime.now())
      }
      return newDeviceSecret

