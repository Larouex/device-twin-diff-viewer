#!/home/Larouex/Python
# ==================================================================================
#   File:   telemetryserver.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    This module instantiates the class TelemetryServer that reads in the
#           IoTCentralPatterns from config.json and emits a pub/sub model for a
#           device to emulate values that map to the model associated with the device.
#
#   Online:   https://github.com/Larouex/device-twin-diff-viewer
#
#   (c) 2021 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)
# ==================================================================================
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from classes.telemetryserver import TelemetryServer

from classes.config import Config

# -------------------------------------------------------------------------------
#   Setup the Telemetry Server for the Device Patterns
# -------------------------------------------------------------------------------
async def setup_server(WhatIf, TelemetryServer):

  try:

    Log.info("[SERVER] setup_server...")
    return await TelemetryServer.setup()

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [setup_server]" )
    return

# -------------------------------------------------------------------------------
#   Start the OPC Server for Multiple Twin and Device Patterns
# -------------------------------------------------------------------------------
async def run_server(WhatIf, TelemetryServer):

  try:

    Log.info("[SERVER] start_server...")
    return await TelemetryServer.run()

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [start_server]" )

  finally:
    await stop_server(WhatIf, TelemetryServer)

# -------------------------------------------------------------------------------
#   Start the OPC Server for Multiple Twin and Device Patterns
# -------------------------------------------------------------------------------
async def stop_server(WhatIf, TelemetryServer):

  try:

    Log.info("[SERVER] stop_server...")
    await TelemetryServer.stop()
    return

  except Exception as ex:
    Log.error("[ERROR] %s" % ex)
    Log.error("[TERMINATING] We encountered an error in [stop_server]" )


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
      print("HELP for telemetryservers.py")
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
  await setup_server(whatif, telemetry_server)
  Log.info("[SERVER] Instance Info (telemetry_server): %s" % telemetry_server)

  # Start the server loop
  await run_server(whatif, telemetry_server)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

