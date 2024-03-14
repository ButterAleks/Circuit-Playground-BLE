# Circuit-Playground-BLE 
## Table of Contents
1. [How to Install](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#how-to-install)
2. [Prerequisites](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#prerequisites)
3. [What is the bluetooth_management Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth_management-library)
4. [How does Bluetooth Low Energy (BLE) Work?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#how-does-bluetooth-low-energy-ble-work)
5. [What is the adafruit_ble Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library)
6. [What is the Bluetooth Manager?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth-manager)
7. [General Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#general-functions)
8. [Peripheral Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#peripheral-functions)
9. [Host Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#host-functions)
10. [Miscellaneous Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#miscellaneous-functions)

## How to Install?
In order to install this on a Bluefruit Circuit Playground, all you'll need to do is install the mpy file either directly from the repo or from an official release and then place it into the lib folder within the storage of the board.

## Prerequisites
This library needs the follow things in order to operate properly:
- Circuit Python
- The adafruit_ble library
- And the _bleio core module that should come with Circuit Python

## What is the bluetooth_management Library?
The bluetooth_management library is a library designed for Adafruit's Bluefruit Circuit Playground, developed in circuit python. I made this library because I was playing around with bluetooth and noticed that adafruit_ble the official library for the board relating to bluetooth was a bit lackluster in terms of features so I decided to make a library that works around it in order to allow for me and other people to actually be able to use the bluetooth capabilities. This library likely won't satisfy everybody and so you're encourage to just play around with it and maybe even work around it by seeing how it works by looking at the code here in the bluetooth_management.py file.

## How does Bluetooth Low Energy (BLE) Work?
If the explanations aren't good enough as this briefly goes over some key concepts needed to understand this documentation, feel free to check the links in footnotes[^1] 1-3 as they contain more information about how BLE works

  ### Discovery[^2]
  Discovering other devices is done via broadcasting advertising packets on 3 seperate channels. These packets are sent multiple times over a period of time called the advertising interval. To reduce the chance of multiple consecutive collisions a random delay of up to 10 miliseconds is added to each advertising interval. A scanner listens during to a channel during a period of time called the scan window, which is periodically repeated every scan interval. Therefore the latency between advertising and discovery is based off the advertising interval, scan window, and the scan interval. 

  ### GATT[^3]
  All BLE devices use GATT, AKA the Generic Attribute Profile which is how BLE devices communicate data about themselves with each other. The following terminology: Host, Peripheral, Service, Characteristic, and Descriptors, are all things related to the GATT of a device.
  - __Host__: Hosts are basically a form of server as multiple Peripherals can connect to a host. (However, this library does not natively support multiple peripherals connected at once so if you want to do that then you'll need to set up your own system to handle them, you'll also probably have to take inspiration from some of the host functions). Hosts can also scan for devices and discover services from another device in order to get characteristics from that device, so that way they can get and or write data to that device.
  - __Peripheral__: Peripherals can advertise data about themselves to be discovered by Hosts. Once connected peripherals will stop advertising as they cannot connect to multiple Hosts. All peripherals can then do over the connection from there is disconnect from the host or read and or write to their characteristics.
  - __Service__: A service is basically a collection of characteristics that all generally have different information about the same thing. An example would be a temperature sensor that has a service that holds characteristics with various kinds of temperature data.
  - __Characterisitic__: A characteristic is a container for data. The data of a characteristic is stored in its `value` property. Characteristics also have specific properties, these are elaborated on in this file when information about them is more relevant, but for now the different types of properties of a characteristic are: `Write No Response`, `Write`, `Read`, `Notify`, `Indicate`, and `Broadcast`.
  - __Descriptor__: A descriptor simply something that provides additional information about a device's characteristic for a human to interpret. A characteristic can have any number of descriptors and descriptors are completely optional when creating characteristics.

## What is the adafruit_ble Library?
The adafruit_ble[^4] library is the offically supported BLE library created by adafruit for the Bluefruit Circuit Playground board for Circuit Python. However, if it weren't for this library than the library you're reading about right now wouldn't exist. This is because there are flaws in the offical library that actually made it kind of impossible to realistically use due to unforseen errors caused by the library so I went ahead and made this so at least people had something that would work with another device. 

> [!IMPORTANT]
> Everything mentioned in this section must be imported from the adafruit_ble library as it is not natively part of the bluetooth_management library. This shouldn't be a problem since the bluetooth_management library needs the adafruit_ble library to function anyway. 

This section will really only cover what this library uses from the adafruit_ble library as that's really the only stuff that matters within the context of this library.

  ### Attributes
  You don't really create any instances of Attributes, you just call the class in order to get various constants needed to provide values for various security levels. The types of security that can be specified with Attributes are as follows:
  - `Attribute.NO_ACCESS`: Indicates that access is not allowed
  - `Attribute.OPEN`: Indicates that there is no security
  - `Attribute.ENCRYPT_NO_MITM`: Indicates unauthenticated encryption, without man-in-the-middle protection
  - `Attribute.ENCRYPT_WITH_MITM`: Indicates authenticated encryption, with man-in-the-middle protection
  - `Attribute.LESC_NO_MITM`: Indicates LESC encryption, with man-in-the-middle protection
  - `Attribute.SIGNED_NO_MITM`: Indicates unauthenticated data signing, without man-in-the-middle protection
  - `Attribute.SIGNED_WITH_MITM`: Indicates authenticated data signing, without man-in-the-middle protection

  ### Advertisements
  Advertisements are how you allow for a peripheral to be discovered, in order to do this you just call a class using it's name like a function. EX `Advertisement()`
  There are various types of advertisements they are as follows:
  - __Advertisement__: The main basic kind of advertisement, has no special properties
  - __ProvideServicesAdvertisement__: This specific advertisement says what services become available upon connection by also passsing in a Service when creating it. EX `ProvideServicesAdvertisement(service)`
  - __SolicitServicesAdvertisement__: This specific advertisement tells other devices what services it would like to work with upon connection and is created similarly to a ProvideServicesAdvertisement but instead this time it's `SolicitServicesAdvertisement(service)`

  All Advertisements inherit from the base Advertisement class, this means all the advertisements have the same base properties. I don't think I can describe those properties any better than the current documentation for the library so just click [here](https://docs.circuitpython.org/projects/ble/en/latest/advertising.html#adafruit_ble.advertising.Advertisement) for more information

## What is the Bluetooth Manager?
The Bluetooth Manager is the main class that holds all the functionality of the library, this was done so that way you only have to import one thing when importing the library. You can make a new instance of the Bluetooth Manager by calling `BluetoothManager()`. It is very not recommended to make multiple instances as this will likely cause conflictions due to there only being one Bluetooth chip on the Circuit Playground.

The variables for the Bluetooth Manager are as follows:
- __bluetooth_mode_peripheral__ _= False_: This boolean is the current mode of the device. If true it means that the device is acting as a peripheral. If false it means that the device is acting as a host.
- __\_radio__ _= BLERadio()_: This variable holds the BLERadio() instance for the Manager however this is meant to be a private varaible as seen with the underscore at the beginning of it's name, so it isn't meant to be accessed by the user
- __ble__ _= None_: This stores the BLEConnection that will be created when a connection to another device is made, the user likely won't need to use this variable but it is public just in case. If you want more information about the BLEConnection object please refer to the adafruit_ble library documentation[^4]

## General Functions
- `get_bluetooth_name() -> string`: This function returns the device name for bluetooth
- `get_bluetooth_transmission_power() -> int`: This function returns the transmission power for bluetooth
- `get_bluetooth_address() -> bytes`: This function returns the address for bluetooth
- `get_bluetooth_advertising_state() -> bool`: This function returns whether or not we're advertising
- `get_bluetooth_connection_state() -> bool`: This function returns whether or not we're connected to another device
- `create_service(uuid: string) -> Service`: This function returns a service created by the uuid specified by the user
  - __uuid: string__: This is a string that should be formatted like a hex code to specify the kind of service you want to make. The type of service you make will not dictate it's characteristics, only how it is identified by other devices. If you need more information to know what hex codes you'll want to use you'll want to refer to the Bluetooth Specifications[^5]

> [!NOTE]
> The propeties of a characteristic determine how the characteristic can be interacted with, they are as follows:
> | Bit (that makes up part of the number) | 6th (most significant bit) | 5th | 4th | 3rd | 2nd | 1st (least signficiant bit) |
> | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | Name | Write No Response | Write | Read | Notify | Indicate | Broadcast |
> | Description | Allows the value of the characteristic to be written too but no response will be sent back | Allows the value of the characteristic to be written too | Allows the value of the characteristic to be read from | Allows host to tell peripheral when it's value has been set by the host | Allows host to tell peripheral when it's value has been set by the host and makes the host wait for a response | Allows the characteristic to show up in advertising packets |
- `add_characteristic_to_service(service: Service, uuid: string, properties: list = [False] * 6, read_perm: Attribute = Attribute.OPEN, write_perm: Attribute = Attribute.OPEN, max_length: int = 20, fixed_length: bool = False, user_description: string = None) -> Characteristic`: This function adds a characteristic to a service and returns it. There is no function to create a characteristic by itself because a characteristic can only be made when it's applied to a service.
  - __service: Service__: The service to add an advertisement to
  - __uuid: string__: This is a string that should be formatted like a hex code to specify the kind of characteristic you want. The type of characteristic you make will not dictate how it's value works, only how it is identified by other devices. If you need more information to know what hex codes you'll want to use you'll want to refer to the Bluetooth Specifications[^5]
  - (optional) __properties: list__ _= [False] * 6_: This is a list of 6 boolean values which will be converted into a number to represent the properties of a characteristic for more information about what booleans mean what look at the note above
  - (optional) __read_perm: Attribute__ _= Attribute.Open_: This represents the access of another device for reading from the characteristic. For information about the Attribute data type please look in the [What is the adafruit_ble Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library) Section of this file.
  - (optional) __write_perm: Attribute__ _= Attribute.Open_: This represents the access of another device for writing to the characteristic. For information about the Attribute data type please look in the [What is the adafruit_ble Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library) Section of this file.
  - (optional) __max_length: int__ _= 20_: The max amount of bytes the value of this characteristic can hold to represent its value
  - (optional) __fixed_length: bool__ _= False_: When true the value of the characteristic will have a fixed length of bytes
  - (optional) __user_description: string__ _= None_: This string allows the creator of the characteristic to provide any user a user-friendly description of the characteristic

> [!NOTE]
> You don't need characteristic buffers or packet buffers in order to read or write to a characteristic. However these are still implemented if a more structured way of working with charactersitic data is desired.
- `create_characteristic_buffer(characteristic: Characteristic, timeout: int = 1, buffer_size: int = 64) -> CharacteristicBuffer`: This function creates and returns a CharacteristicBuffer. A CharacteristicBuffer is a buffer that stores data from a characteristic when it is told to read from the characteristic.
  - __characteristic: Characteristic__: The characteristic for the buffer to read from
  - (optional) __timeout: int__ _= 1_: The time that the characteristic waits in seconds between characters
  - (optional) __buffer_size: int__ _= 64_: The total amount of bytes that can represent the data within the buffer.

- `create_packet_buffer(characteristic: Characteristic, buffer_size: int, max_packet_size: int) -> PacketBuffer`: This function creates and returns a PacketBuffer. A PacketBuffer is a buffer that writes data to a characteristic when it is told to read from the characteristic.
  - __characteristic: Characteristic__: The characteristic for the buffer to read from
  - (optional) __buffer_size: int__: The total amount of bytes that can represent the data within the buffer.
  - (optional) __max_packet_size: int__: The total amount of bytes that a single packet can hold (this overrides the characteristic).

- `read_from_characteristic_with_buffer(read_buffer: CharacteristicBuffer) -> bytes`: This function allows the user to read data from a characteristic with a CharacteristicBuffer and return as a sequence of bytes.
  - __read_buffer: CharacteristicBuffer__: This is the buffer that is used to read data from a characteristic.

- `read_from_characteristic(characteristic: Characteristic) -> bytearray`: This function allows the user to read data from a characteristic and return as an array of bytes.
  - __characteristic: Characteristic__: This is the characteristic that will be read from

- `write_to_characteristic_with_buffer(write_buffer: PacketBuffer, message: string, max_length: int = 20, clear_buffer: bool = True) -> int`: This allows the user to write to a characteristic using a PacketBuffer. This returns the total amount of bytes written to the characteristic.
  - __write_buffer: PacketBuffer__: The packet buffer that will be used to write to a characterisitic
  - __message: string__: The message to write to the characteristic.
  - (optional) __max_length: int__ _= 20_: The max length of bytes that the characteristic can hold
  - (optional) __clear_buffer: bool__ _= True_: If true this will clear the buffer before writing to it

- `write_to_characteristic(characteristic: Characteristic, message: string, max_length: int = 20, clear_buffer: bool = True) -> bytearray`: This allows the user to write to a characteristic. This returns the value of the characteristic after it has been written to as an array of bytes
  - __write_buffer: PacketBuffer__: The packet buffer that will be used to write to a characterisitic
  - __message: string__: The message to write to the characteristic.
  - (optional) __max_length: int__ _= 20_: The max length of bytes that the characteristic can hold
  - (optional) __clear_buffer: bool__ _= True_: If true this will clear the buffer before writing to it (in this case the buffer is the value of the characteristic)

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
  - (optional) __filters: list__ _= []_: This is a list of strings that should contain the hex codes of services that the user wishes to find. If you need more information to know what hex codes you'll want to use you'll want to refer to the Bluetooth Specifications[^5]

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

[^1]: [How does BLE Work?](https://www.spiceworks.com/tech/iot/articles/what-is-bluetooth-le/#_001)
[^2]: [More detail on how Advertising works for BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy#Advertising_and_discovery)
[^3]: [More detail on how GATT works for BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy#Software_model)
[^4]: [adafruit_ble documentation](https://docs.circuitpython.org/projects/ble/en/latest/api.html#adafruit_ble)
[^5]: [Bluetooth Specifications](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1705211162426)
