# Circuit-Playground-BLE 
## Table of Contents
1. [What is the bluetooth_management Library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth_management-library)
2. [How does Bluetooth Low Energy (BLE) Work?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#how-does-bluetooth-low-energy-ble-work)
3. [What is the adafruit_ble library?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-adafruit_ble-library)
4. [What is the Bluetooth Manager?](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#what-is-the-bluetooth-manager)
5. [General Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#general-functions)
6. [Peripheral Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#peripheral-functions)
7. [Host Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#host-functions)
8. [Miscellaneous Functions](https://github.com/ButterAleks/Circuit-Playground-BLE/blob/main/README.md#miscellaneous-functions)

## What is the bluetooth_management Library?


## How does Bluetooth Low Energy (BLE) Work?


## What is the adafruit_ble library?


## What is the Bluetooth Manager?


## General Functions


## Peripheral Functions


## Host Functions


## Miscellaneous Functions
> [!NOTE]
> The propeties of a characteristic determine how the characteristic can be interacted with, they are as follows:
> | Bit (that makes up part of the number) | 6th (most significant bit) | 5th | 4th | 3rd | 2nd | 1st (least signficiant bit) |
> | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | Name | Write No Response | Write | Read | Notify | Indicate | Broadcast |
> | Description | Allows the value of the characteristic to be written too but no response will be sent back | Allows the value of the characteristic to be written too | Allows the value of the characteristic to be read from | Allows host to tell peripheral when it's value has been set by the host | Allows host to tell peripheral when it's value has been set by the host and makes the host wait for a response | Allows the characteristic to show up in advertising packets |
- `convert_properties_to_num(properties: list) -> int`: This function takes in a list of 6 boolean values in order to convert them into a number to represent the properties of a characteristic for more information look at the note above
  - __list__: a list of 6 boolean values ordered in the same way the bits of the properties number are. Set them to true to activate the property or false to deactivate the property when using the number to set the properties of a characteristic
- `convert_num_to_properties(num: int) -> list`: This function takes in a number in order to convert it into a list of 6 boolean values to represent the properties of a characteristic for more information look at the note at the top of this section
  - __num__: a number that represents the properties of a characteristic. Each of the 6 bits of this number represent one of the six properties of the characteristic
