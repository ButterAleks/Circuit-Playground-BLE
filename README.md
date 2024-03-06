# Circuit-Playground-BLE 
## Table of Contents
1. [What is the bluetooth_management Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth_management-library)
2. [How does Bluetooth Low Energy (BLE) Work?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#how-does-bluetooth-low-energy-ble-work)
3. [What is the adafruit_ble Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library)
4. [What is the Bluetooth Manager?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth-manager)
5. [General Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#general-functions)
6. [Peripheral Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#peripheral-functions)
7. [Host Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#host-functions)
8. [Miscellaneous Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#miscellaneous-functions)

## What is the bluetooth_management Library?


## How does Bluetooth Low Energy (BLE) Work?


## What is the adafruit_ble Library?


## What is the Bluetooth Manager?


## General Functions


## Peripheral Functions
> [!NOTE]
> Once a connection to a device acting as a peripheral is made all of it's advertisements will stop broadcasting. This means that to connect to another device after a previous connection, you will need to start advertising again.
- `start_advertising(advertisement: Advertisement)`: Begins sending out an advertisement as a peripheral.
  - __advertisement: Advertisement__: This is an advertisement that should be created that the user that is then able to be picked up on by other Bluetooth devices. (For more information on how to make advertisements please look within the [What is the adafruit_ble Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library) Section of this file)
- `stop_advertising()`: This will stop any currently active advertisements from continuing to be sent out

## Host Functions
- `start_scanning(advertisements_to_collect: int = 10, buffer_size: int = 512, extended: bool = False, timeout: float = None, interval: float = 0.1, window: float = 0.1, minimum_rssi: int = -80, filter_no_name: bool = True, active: bool = True, print_debug: bool = False) -> dict`: This function allows a device acting as a host to start scanning for peripheral devices. This function returns a dictionary who's keys are the names of the devices found and the values are the addresses which can be used to connect to the devices.
  -(optional)  __advertisements_to_collect: int__ _= 10_: This is the maximum amount of advertisements that can be collected before the function automatically exits. This was implemented for memory reasons with the Circuit Playground due to the board's limited memory
  - (optional) __buffer_size: int__ _= 512_: This the amount of bytes the buffer that holds the collected advertisement data has.
  - (optional) __extended: bool__ _= False_: When set to true extended advertising packets are supported, it's also recommended that you increase buffer_size if this is set to true
  - (optional) __timeout: float__ _= None_: How long until the scan automatically stops, if None then you'll need to call stop_scanning() in order to stop the scan
> [!IMPORTANT]
> This value must be inbetween the range of 0.025 - 40.959375
  - (optional) __interval: float__ _= 0.1_: The interval of time between two consecutive scan windows.
> [!IMPORTANT]
> This value must be <= the value of interval
  - (optional) __window: float__ _= 0.1_: The duration in seconds to scan a BLE channel.
  - (optional) __minimum_rssi: int__ _= -80_: The minimum rssi of devices to return
  - (optional) __filter_no_name: bool__ _= True_: If true this will filter out any advertisements that don't have a name
  - (optional) __active: bool__ _= True_: Allows scan to actually request and retrieve scan responses (Not sure why you'd want to turn this off, but the option is here)
  - (optional) __print_debug: bool__ _= False_: If true, debug information about the scan will be printed to the console
> [!TIP]
> It is recommended that this function is called before calling start_scanning() to prevent any reseting without terminating a scan from preventing further scans
- `stop_scanning()`: This function will stop any currently active scan
> [!NOTE]
> There is an internal reference within the BluetoothManager to store the current BLEConnection, this is important to know as it makes manually storing the connection kind of irrelevant and explains how other functions work without a BLEConnection being passed in the arguments.
- `connect(detected_devices: dict, device_name: string, print_debug: bool = False) -> BLEConnection`: This function allows a device acting as a host to connect to a peripheral device from a dictionary formatted like what start_scanning() returns. The device is specified by device_name. (which is case sensitive) This function returns a BLEConnection which allows you to do things including disconnect from the specified device. There is an internal reference to the current BLEConnection so there isn't really a need to store this value however.
  - __detected_devices: dict__: This is a dictionary that is formatted just like the dictionary returned from start_scanning(). This means that its keys are the names of peripheral devices and its values are the addresses of those peripheral devices.
  - __device_name: string__: This is how you specify the name of the device that you want to connect too, the string should match one of the keys within detected_devices which also means it's case sensitive
  - (optional) __print_debug: bool__ _= False_: When true the function will print debug information about connecting to the specified device
- `disconnect(print_debug: bool = False)`: This function allows you to disconnect from a connected peripheral device.
  - (optional) __print_debug: bool__ _= False_: When true the function will print debug information about disconnecting from the currently connected device
> [!IMPORTANT]
> This function requires a peripheral device to be connected in order to work!
- `discover_device_services(filters: list = []) -> tuple`: This function will return a tuple of discovered services found from a connected device.
> [!NOTE]
> The Bluetooth Specifications are just general guidelines. This means that a specific service may not contain what you expect or may not even be within the specifications. This is important to be aware of if you're struggling to find the data you want.
  - (optional) __filters: list__ _= []_: This is a list of strings that should contain the hex codes of services that the user wishes to find. If you need more information to know what hex codes you'll want to use you'll want to refer to the [Bluetooth Specifications](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1705211162426)

## Miscellaneous Functions
> [!NOTE]
> The propeties of a characteristic determine how the characteristic can be interacted with, they are as follows:
> | Bit (that makes up part of the number) | 6th (most significant bit) | 5th | 4th | 3rd | 2nd | 1st (least signficiant bit) |
> | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | Name | Write No Response | Write | Read | Notify | Indicate | Broadcast |
> | Description | Allows the value of the characteristic to be written too but no response will be sent back | Allows the value of the characteristic to be written too | Allows the value of the characteristic to be read from | Allows host to tell peripheral when it's value has been set by the host | Allows host to tell peripheral when it's value has been set by the host and makes the host wait for a response | Allows the characteristic to show up in advertising packets |
- `convert_properties_to_num(properties: list) -> int`: This function takes in a list of 6 boolean values in order to convert them into a number to represent the properties of a characteristic for more information look at the note above
  - __properties: list__: a list of 6 boolean values ordered in the same way the bits of the properties number are. Set them to true to activate the property or false to deactivate the property when using the number to set the properties of a characteristic
- `convert_num_to_properties(num: int) -> list`: This function takes in a number in order to convert it into a list of 6 boolean values to represent the properties of a characteristic for more information look at the note at the top of this section
  - __num: int__: a number that represents the properties of a characteristic. Each of the 6 bits of this number represent one of the six properties of the characteristic
