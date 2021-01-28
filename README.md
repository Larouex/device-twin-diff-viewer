# Azure IoT Central Device Twin Scenario Viewer
The Device Twin Scenario Viewer is a standalone project that is designed assist device developers and testers who are using the forms and update mechanisms in Azure IoT Central. 
## Project Overview

* <b>Powerful Emulation</b> - Dynamic Configuration of Devices, Nodes and Variables allow you to emulate complex "Digital Twin" topologies. In this project we are working with instances of appliances in a commercial kitchen.
* <b>Azure IoT Central SaaS Integration</b> - Azure IoT Central is our Software as a Service (SaaS) 'Application Platform' that provides telemetry, device management and rich data visualizations. That is just a small part of what it can do. We want to provide you with a way to understand and leverage these features with little coding, some configuration and tons of power!

## Project Capabilities
The capabilities of this project are defined by the various project lifecycle that you configure and prepare your Device and solution on the Azure IoT Central Application platform.

* <b>Pub/Sub Telemetry Server</b> - Configuration of the components, interfaces and variables for generating telemetry that can be subscribed by your device fleet.
* <b>Device Fleet Provisioning</b> - Configuration of the devices and models supporting provisioning into your Azure IoT Central application.
* <b>Device Fleet Simulation</b> - Configuration of simulation of the devices and subscribing to the Telemetry Server to send real-world telemetry values and firmware simulation for handling changes to the properties (Twins) and code for handling state changes from property setting, etc.
* <b>Twin History and Diff Viewer</b> - Dashboard viewer that provides a historical view and comparison diff for Twin changes (Desired and Reported)
## Contents
- [Azure IoT Central Device Twin Scenario Viewer](#azure-iot-central-device-twin-scenario-viewer)
  - [Project Overview](#project-overview)
  - [Project Capabilities](#project-capabilities)
  - [Contents](#contents)
  - [Intended Audience for this Project?](#intended-audience-for-this-project)
  - [Requirements for this Project](#requirements-for-this-project)
  - [The Smart Kitchen Overview](#the-smart-kitchen-overview)
    - [HVAC](#hvac)
    - [Walk In Freezer](#walk-in-freezer)
    - [Walk In Refrigerator](#walk-in-refrigerator)
    - [Standing Freezer](#standing-freezer)
    - [Standing Refrigerator](#standing-refrigerator)
    - [Fryer](#fryer)
    - [Cold Table](#cold-table)
    - [Dishwasher](#dishwasher)
## Intended Audience for this Project?
* System Integrators
* Developers
* Administrators of an IoT Central Application
## Requirements for this Project
The requirements and preparations are assumed for this project...

* You have an Azure Account

## The Smart Kitchen Overview
The core of this demo application for Azure IoT Central is the emulation of IoT in the context of a commercial kitchen. We have included the following emulated appliance models that you would find in a commercial kitchen...
### HVAC
![alt text](./Assets/commercial-hvac-header.png "HVAC System")

[LINK: Detailed Overview for the Kitchen HVAC System](./readme_docs/hvac-system-overview.md)

    Measurements
    ---------------------------------
    * Airflow Temperature
    * Main Motor RPM
    * CFM

    Baselines and Trends
    ---------------------------------
    * Ideal Temperature = 68 F
    * Main Motor RPM > Trend
    * CFM > Trend

### Walk In Freezer
![alt text](./Assets/commercial-walkin-freezer-header.png "Walk In Freezer")

[LINK: Detailed Overview for the Walk In Freezer](./readme_docs/walkin-freezer-overview.md)

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

### Walk In Refrigerator
![alt text](./Assets/commercial-walkin-fridge-header.png "Walk In Refrigerator") 

[LINK: Detailed Overview for the Walk In Refrigerator](./readme_docs/walkin-refrigerator-overview.md)

    Measurements
    ---------------------------------
    Temperature
    Humidity
    Door Open Count
    Door Ajar
    Compressor Health

    Baselines and Trends
    ---------------------------------
    Ideal Temperature = 39 F
    Ideal Humidity = 65 RH
    Door Open Count is a Trend
    Door Ajar is a Trend
    Compressor Health > 98

### Standing Freezer
![alt text](./Assets/commercial-standing-freezer-header.png "Standing Freezer")

[LINK: Detailed Overview for the Standing Freezer](./readme_docs/standing-freezer-overview.md)

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

### Standing Refrigerator
![alt text](./Assets/commercial-standing-fridge-header.png "Standing Refrigerator")

[LINK: Detailed Overview for the Standing Refrigerator](./readme_docs/standing-refrigerator-overview.md)

    Measurements
    ---------------------------------
    Temperature
    Humidity
    Door Open Count
    Door Ajar
    Compressor Health

    Baselines and Trends
    ---------------------------------
    Ideal Temperature = 39 F
    Ideal Humidity = 65 RH
    Door Open Count is a Trend
    Door Ajar is a Trend
    Compressor Health > 98

### Fryer
![alt text](./Assets/commercial-fryer-header.png "Fryer")

[LINK: Detailed Overview for the Fryer](./readme_docs/fryer-overview.md)

    Measurements
    ---------------------------------
      Temperature
      Oil Quality
      Fryer Heater Health

    Baselines and Trends
    ---------------------------------
      Ideal Temperature = 350-360 F
      Oil Quality > 75
      Fryer Heater Health > 98

### Cold Table
![alt text](./Assets/commercial-cold-table.png "Cold Table")

[LINK: Detailed Overview for the Cold Table](./readme_docs/cold-table-overview.md)

    Measurements
    ---------------------------------
      Temperature
      Compressor Health

    Baselines and Trends
    ---------------------------------
      Ideal Temperature = 39 F
      Compressor Health > 98

### Dishwasher
![alt text](./Assets/commercial-dishwasher.png "Dishwasher")

[LINK: Detailed Overview for the Dishwasher](./readme_docs/dishwasher-overview.md)

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
