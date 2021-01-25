
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
      self.config = {}
      self.load_config()

      # Symmetric Key
      self.symmetrickey = SymmetricKey(self.logger)

      # Secrets
      self.secrets = Secrets(self.logger)
      self.secrets_cache_data = self.secrets.data

      # meta
      self.application_uri = None
      self.namespace = None
      self.device_name = None
      self.device_capability_model_id = None
      self.device_capability_model = []
      self.device_name_prefix = None
      self.ignore_interface_ids = []

      # Devices Cache
      self.devices_cache = DevicesCache(self.logger)
      self.devices_cache_data = self.devices_cache.data
      self.device_to_provision = []


    # -------------------------------------------------------------------------------
    #   Function:   provision_devices
    #   Usage:      Grabs the Defined Devices and Provisions into IoT Central
    #               a provisioning call to associated a device template to the node
    #               interface based on the twin, device or gateway pattern
    # -------------------------------------------------------------------------------
    async def provision_devices(self):

      # First up we gather all of the needed provisioning meta-data and secrets
      try:

        self.namespace = self.config["Model"]["NameSpace"]
        self.device_capability_model_id = self.config["Model"]["DeviceCapabilityModelId"]
        self.device_name_prefix = self.config["Device"]["DeviceNamePrefix"]

        # this is our working cache for things we provision in this session
        self.device_to_provision = self.create_device_to_provision()
        self.device_create()

        print("********************************")
        print("DEVICE TO PROVISION: %s" % self.device_to_provision)
        print("********************************")

        # Azure IoT Central SDK Call to create the provisioning_device_client
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
          provisioning_host = self.secrets.get_provisioning_host(),
          registration_id = self.device_to_provision["Device"]["Name"],
          id_scope = self.secrets.get_scope_id(),
          symmetric_key = self.device_to_provision["Device"]["Secrets"]["DeviceSymmetricKey"],
          websockets=True
        )

        # Azure IoT Central SDK call to set the DCM payload and provision the device
        provisioning_device_client.provisioning_payload = '{"iotcModelId":"%s"}' % (self.device_to_provision["Device"]["DeviceCapabilityModelId"])
        registration_result = await provisioning_device_client.register()
        self.logger.info("[REGISTRATION RESULT] %s" % registration_result)
        self.logger.info("[DeviceSymmetricKey] %s" % self.device_to_provision["Device"]["Secrets"]["DeviceSymmetricKey"])
        self.device_to_provision["Device"]["Secrets"]["AssignedHub"] = registration_result.registration_state.assigned_hub
        self.devices_cache.update_file(self.device_to_provision)
        self.secrets.update_file_device_secrets(self.device_to_provision)
        

        print("********************************")
        print("DEVICE SUCCESSFULLY PROVISIONED: %s" % self.device_to_provision)
        print("********************************")

        return

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in CLASS::ProvisionDevice::provision_device()" )

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration
    # -------------------------------------------------------------------------------
    def load_config(self):

      config = Config(self.logger)
      self.config = config.data
      return

    # -------------------------------------------------------------------------------
    #   Function:   device_create
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def device_create(self):

      try:
        
        self.device_name = self.device_name_prefix.format(id=self.id_device)
        self.device_capability_model_id = self.config["Model"]["DeviceCapabilityModelId"]
        self.device_to_provision["Device"] = self.create_device_capability_model()
        self.device_to_provision["Device"]["Secrets"] = self.create_device_connection()
        print("here")
        print(self.device_to_provision)

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in CLASS::ProvisionDevices::devices_create()" )

        return

    # -------------------------------------------------------------------------------
    #   Function:   create_device_to_provision`
    #   Usage:      Returns a Devices Array
    # -------------------------------------------------------------------------------
    def create_device_to_provision(self):
      newDeviceToProvisionArray = {
        "Device": {
          "Secrets": {
          }
        }
      }
      return newDeviceToProvisionArray

    # -------------------------------------------------------------------------------
    #   Function:   create_device_capability_model
    #   Usage:      Returns a Device Interface with the  Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_capability_model(self):
      newDeviceCapabilityModel = {
        "Name": self.device_name,
        "DeviceCapabilityModelId": self.device_capability_model_id,
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
        "DeviceCapabilityModelId": self.device_capability_model_id,
        "AssignedHub": "",
        "DeviceSymmetricKey": device_symmetric_key,
        "LastProvisioned": str(datetime.datetime.now())
      }
      return newDeviceSecret

