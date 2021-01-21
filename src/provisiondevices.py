# ==================================================================================
#   File:   provisiondevices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Provision a Device in IoT Central
#
#   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from classes.provisiondevice import ProvisionDevice
from classes.config import Config

# -------------------------------------------------------------------------------
#   Provision Device
# -------------------------------------------------------------------------------
async def provision_devices(Id):

  provisiondevices = ProvisionDevices(Log, Id)
  await provisiondevices.provision_devices()
  return True

async def main(argv):

    # execution state from args
    id = 1

    short_options = "hvdr:"
    long_options = ["help", "verbose", "debug", "registerid="]
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))

    for current_argument, current_value in arguments:
      if current_argument in ("-h", "--help"):
        print("------------------------------------------------------------------------------------------------------------------------------------------")
        print("HELP for provisiondevices.py")
        print("------------------------------------------------------------------------------------------------------------------------------------------")
        print("")
        print("  BASIC PARAMETERS...")
        print("")
        print("  -h or --help - Print out this Help Information")
        print("  -v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
        print("  -d or --debug - Debug Mode with lots of DEBUG Data will be Output to Assist with Tracing and Debugging")
        print("")
        print("  OPTIONAL PARAMETERS...")
        print("")
        print("    -r or --registerid - This numeric value will get appended to your provisioned device. Example '1' would result in larouex-smart-kitchen-1")
        print("       USAGE: -r 5")
        print("       DEFAULT: 1")
        print("")
        print("------------------------------------------------------------------------------------------------------------------------------------------")
        return

      if current_argument in ("-v", "--verbose"):
        Log.basicConfig(format="%(levelname)s: %(message)s", level = Log.INFO)
        Log.info("Verbose Logging Mode...")
      else:
        Log.basicConfig(format="%(levelname)s: %(message)s")

      if current_argument in ("-d", "--debug"):
        Log.basicConfig(format="%(levelname)s: %(message)s", level = Log.DEBUG)
        Log.info("Debug Logging Mode...")
      else:
        Log.basicConfig(format="%(levelname)s: %(message)s")

      if current_argument in ("-r", "--registerid"):
        id = current_value
        Log.info("Register Id is Specified as: {id}".format(id = id))

        # validate the number is a NUMBER
        if (id.isnumeric() == False):
          print("[ERROR] -r --registerid must be a numeric value")
          return

    await provision_device(id)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

