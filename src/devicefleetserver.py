#!/home/Larouex/Python
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
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from classes.devicefleetserver import DeviceFleetServer
from classes.telemetryserver import TelemetryServer
from classes.config import Config

# -------------------------------------------------------------------------------
#   Setup the Telemetry Server for the Device Patterns
# -------------------------------------------------------------------------------
async def setup_telemetry_server(TelemetryServer):

  try:
    return await TelemetryServer.setup()

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [setup_telemetry_server]" )
    return

# -------------------------------------------------------------------------------
#   Start the Device Fleet which in turn starts the Telemetry Server
# -------------------------------------------------------------------------------
async def run_fleet(DeviceFleetServer, TelemetryServer):

  try:
    return await DeviceFleetServer.run(TelemetryServer)

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [run_server]" )


# -------------------------------------------------------------------------------
#   main()
# -------------------------------------------------------------------------------
async def main(argv):

  # execution state from args
  short_options = "hvd"
  long_options = ["help", "verbose", "debug"]
  full_cmd_arguments = sys.argv
  argument_list = full_cmd_arguments[1:]
  try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
  except getopt.error as err:
    print (str(err))

  for current_argument, current_value in arguments:

    if current_argument in ("-h", "--help"):
      print("------------------------------------------------------------------------------------------------------------------------------------------")
      print("HELP for devicefleetserver.py")
      print("------------------------------------------------------------------------------------------------------------------------------------------")
      print("")
      print("  BASIC PARAMETERS...")
      print("")
      print("  -h or --help - Print out this Help Information")
      print("  -v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
      print("  -d or --debug - Debug Mode with lots of DEBUG Data will be Output to Assist with Tracing and Debugging")
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

  # Configure Server
  telemetry_server = TelemetryServer(Log)
  await setup_telemetry_server(telemetry_server)
  Log.info("[SERVER] Instance Info (telemetry_server): %s" % telemetry_server)

  # Configure & Start DeviceFleet
  device_fleet_server = DeviceFleetServer(Log)
  await run_fleet(device_fleet_server, telemetry_server)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

