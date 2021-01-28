# Dishwasher - Smart Kitchen OPC-UA Integration with Azure IoT Central
![alt text](./Assets/commercial-dishwasher.png "Dishwasher")

This is a detailed overview of the following...

* <b>The Configuration for the OPC-UA Server</b> We will show the details of the configuration for emulation of the Server, Nodes and Variables for the OPC-UA Server.
* <b>Telemetry</b> The Telemetry that we are emulating.
* <b>Plug and Play Model</b> The Azure Plug and Play Model we are using with IoT Central.

## Dishwasher

    Measurements
    ---------------------------------
      Heating Element Health
      Motor Health
      Wash Cycles
      Temperature

    Baselines and Trends
    ---------------------------------
      Ideal Temperature = 180-185 F
      Heating Element Health > 98
      Motor Health > 98
      Wash Cycles - Trend Count
