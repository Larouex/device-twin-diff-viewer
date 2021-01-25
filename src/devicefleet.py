#!/home/Larouex/Python
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
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from classes.devicefleet import DeviceFleet
from classes.telemetryserver import TelemetryServer
from classes.config import Config

# -------------------------------------------------------------------------------
#   Setup the Telemetry Server for the Device Patterns
# -------------------------------------------------------------------------------
async def setup_telemetry_server(WhatIf, TelemetryServer):

  try:

    Log.info("[DEVICEFLEET] Setting up Telemetry Server...")
    return await TelemetryServer.setup()

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [setup_telemetry_server]" )
    return

# -------------------------------------------------------------------------------
#   Start the Device Fleet which in turn starts the Telemetry Server
# -------------------------------------------------------------------------------
async def run_fleet(WhatIf, DeviceFleet, TelemetryServer):

  try:

    Log.info("[DEVICEFLEET] Starting Device Fleet...")
    return await DeviceFleet.run(TelemetryServer)

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [run_server]" )


# -------------------------------------------------------------------------------
#   main()
# -------------------------------------------------------------------------------
async def main(argv):

  # parameters
  whatif = False

  # execution state from args
  short_options = "hvdw"
  long_options = ["help", "verbose", "debug", "whatif"]
  full_cmd_arguments = sys.argv
  argument_list = full_cmd_arguments[1:]
  try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
  except getopt.error as err:
    print (str(err))

  for current_argument, current_value in arguments:

    if current_argument in ("-h", "--help"):
      print("------------------------------------------------------------------------------------------------------------------------------------------")
      print("HELP for devicefleet.py")
      print("------------------------------------------------------------------------------------------------------------------------------------------")
      print("")
      print("  BASIC PARAMETERS...")
      print("")
      print("  -h or --help - Print out this Help Information")
      print("  -v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
      print("  -d or --debug - Debug Mode with lots of DEBUG Data will be Output to Assist with Tracing and Debugging")
      print("  -w or --whatif - Combine with Verbose it will Output the Configuration sans starting the Server")
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

    if current_argument in ("-w", "--whatif"):
      whatif = True
      Log.info("WhatIf Mode...")

  # Configure Server
  telemetry_server = TelemetryServer(Log, whatif)
  await setup_telemetry_server(whatif, telemetry_server)
  Log.info("[SERVER] Instance Info (telemetry_server): %s" % telemetry_server)

  # Configure & Start DeviceFleet
  device_fleet = DeviceFleet(Log, whatif)
  await run_fleet(whatif, device_fleet, telemetry_server)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

