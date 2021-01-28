# Getting Started with your Development Environment
This document helps you get your development environment ready for writing code for the project. The development "toolchain" refers to all of the various tools, SDK's and bits we need to install on your machine to facilitate a smooth experience. 

## OPC Server Overview and Features

This is a OPC Server written in Python using the opcua-asyncio that is based on the popular FreeOpcUa project/library. We have added implementations to Azure IoT Central using the Azure IoT SDK for Python.

Here are links for reference (<i>no need to install anything yet</i>)

* [LINK: Azure IoT SDKs for Python](https://github.com/Azure/azure-iot-sdk-python)
* [LINK: opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio)

One important thing to note as you work through the tutorial here: If you are coming from the IoT Device world, the terminology of OPC is very different and vice-versa from OPC to Azure IoT Central. I will give simple, high level explanations, but be aware of those differences. The easist way to think about the assumptions we are making in the context of this tutorial...

| OPC | Azure IoT | Represented in Azure IoT Central |
|---|---|---|
| Node | Device Interface | Interface in the Device Capability Model |
| Variable | Telemetry | Telemetry Items in the Device Interface  |
| OPC Server | Device | We represent the OPC Server as a Device in IoT Central  |

The OPC Server implements two Nodes...

  * Ambient
  * Process

The table below shows the Variables (Telemetry) per Node and the Sequence of the data that is published by the OPC Server.
| Node | Variables | Data Type | Sequence of Data |
|---|---|---|---|
| Ambient | Temperature | Float | 72.45,73.23,85.90,91.54,73.28,67.54,69.28,81.54,73.68,81.23 |
| Ambient | Humidity | Float | 68.8,71.0,72.3,64.1,89.2,67.3 |
| Process | Temperature | Float | 112.45,113.23,115.90,121.54,143.28,151.23 |
| Process | Pressure | Integer | 157,151,223,289,190,162,203,209,154,299 |
| Process | Mixing Ratio | Float | 9.6,12.9,13.4,10.2,9.9,13.2 |

## Setting up Your Development Toolchain
The code in this repository depends on Visual Studio Code and Python.

### Your Local Machine
The development "toolchain" refers to all of the various tools, SDK's and bits we need to install on your machine to facilitate a smooth experience developing our project. Our main development tool will be Visual Studio code. 

This project was developed on Python version 3.8.5 and you should be using the latest version of Python as certain libraries like asyncio may not work in older versions.


| - | Install These Tools |
|---|---|
| ![Python](./Assets/python-icon-100.png) | [LINK: Python 3 Installation Page](https://www.python.org/downloads/) - Python is the programming language we will use to build our applications. |
| ![Visual Studio Code](./Assets/vs-code-icon-100.png) | [LINK: Visual Studio Code Installation Page](https://code.visualstudio.com/download) - Visual Studio Code is a lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux. This is the IDE we will use to write code and deploy to the our BLE Devices and the Raspberry Pi Gateway.  |

### Install all the Tools for Visual Studio Code
These are a set of tools we will use to develop our apps. You can open the Extensions sidebar with "Shift+Ctrl+X) or click the icon in the side navigator bar.

![alt text](./Assets/vs-code-python-sml.png "VS Code Python")


### Clone this project "IoTC-OPCUA-Server-Basic"...
Find a working folder for this project on your machine...
````bash
git clone https://github.com/Larouex/IoTC-OPCUA-Server-Basic.git
cd IoTC-OPCUA-Server-Basic
pip3 install -r requirements.txt
````

Open the "IoTC-OPCUA-Server-Basic" folder in Visual Studio Code.

## Install the "UaExpert — A Full-Featured OPC-UA Client"
[LINK: OPC UA Client – Overview](https://www.unified-automation.com/products/development-tools/uaexpert.html)

The UaExpert® is a full-featured OPC-UA Client demonstrating the capabilities of C++ OPC-UA Client SDK/Toolkit. The UaExpert is designed as a general purpose test client supporting OPC-UA features like DataAccess, Alarms & Conditions, Historical Access and calling of UA Methods.

Install the Client from here...
[LINK: OPC UA Clients – Downloads](https://www.unified-automation.com/downloads/opc-ua-clients.html)

## We are now ready!
