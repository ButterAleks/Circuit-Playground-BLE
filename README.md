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
> The propeties of a characteristic determine how the characteristic can be interacted with, they are as follows
> | Bit (that makes up part of the number) | 6th (most significant bit) | 5th | 4th | 3rd | 2nd | 1st (least signficiant bit) |
> | --- | --- | --- | --- | --- | --- | --- |
> | Name | Write No Response | Write | Read | Notify | Indicate | Broadcast |
> | --- | --- | --- | --- | --- | --- | --- |
> | Description | | | | | | | |
- `convert_properties_to_num(properties: list) -> int`: This function takes in a list of 6 boolean values in order to convert them into a number to represent the properties of a characteristic for more information look at the note above
  - 
