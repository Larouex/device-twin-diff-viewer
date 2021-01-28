# Standing Freezer - Smart Kitchen OPC-UA Integration with Azure IoT Central
![alt text](./Assets/commercial-standing-freezer-header.png "Standing Freezer")

This is a detailed overview of the following...

* <b>The Configuration for the OPC-UA Server</b> We will show the details of the configuration for emulation of the Server, Nodes and Variables for the OPC-UA Server.
* <b>Telemetry</b> The Telemetry that we are emulating.
* <b>Plug and Play Model</b> The Azure Plug and Play Model we are using with IoT Central.

## Standing Freezer

    Measurements
    ---------------------------------
    Temperature
    Humidity
    Door Open Count
    Door Ajar
    Compressor Health

    Baselines and Trends
    ---------------------------------
    Ideal Temperature = 0 F
    Ideal Humidity = 100 RH
    Door Open Count is a Trend
    Door Ajar is a Trend
    Compressor Health > 98
