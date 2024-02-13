#
# Libraries
#

import time
import board
import _bleio
import random
import digitalio
from _bleio import UUID
from _bleio import Service
from _bleio import RoleError
from _bleio import Attribute
from _bleio import PacketBuffer
from _bleio import Characteristic
from _bleio import BluetoothError
from adafruit_ble import BLERadio
from adafruit_ble import BLEConnection
from _bleio import CharacteristicBuffer
from adafruit_circuitplayground import cp
from adafruit_ble.advertising.standard import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

#
# Functions
#

#
# General Functions
#

# Set if we are acting as a host or a peripheral

# Get our name for bluetooth
def get_bluetooth_name() -> string:
    return _radio.name

# Get our transmission power
def get_bluetooth_transmission_power() -> int:
    return _radio.tx_power

# Get our bluetooth address
def get_bluetooth_address() -> bytes:
    return _radio.address_bytes

# Get our current state of advertising
def get_bluetooth_advertising_state() -> bool:
    return _radio.advertising

# Get our current state of connection
def get_bluetooth_connection_state() -> bool:
    return _radio.connected

# Create a service specified by it's UUID
def create_service(uuid: string) -> Service:
    return Service(UUID(int(uuid)))

# This acts as a way to create characteristics as they have to be added to services upon creation
#
# service -> Service: The service to add too
# uuid -> string: The uuid to specify the type of new characteristic
# (optional) properties -> bool[6] = [False] * 6: A list of booleans that specify the properties of the characteristic
# these are as follows from index 0-5; Write No Response, Write, Read, Notify, Indicate, Broadcast
# (optional) read_perm -> Attribute = Attribute.OPEN: Specifys default reading permissions for all connections
# (optional) write_perm -> Attribute = Attribute.OPEN: Specifys default writing permissions for all connections
# (optional) max_length -> int = 20: The max length of a packet that can be written or read from the characteristic
# (optional) fixed_length -> bool = False: Whether or not the length of a packet has to be a fixed amount
# (optional) user_description -> string = None: A defined description for the characteristic
def add_characteristic_to_service(service: Service, uuid: string, properties: list = [False] * 6, read_perm: Attribute = Attribute.OPEN, write_perm: Attribute = Attribute.OPEN, max_length: int = 20, fixed_length: bool = False, user_description: string = None) -> Characteristic:
    return Characteristic.add_to_service(service, UUID(int(uuid)), properties=_convert_properties_to_num(properties), read_perm=read_perm, write_perm=write_perm, max_length=max_length, fixed_length=fixed_length, user_description=user_description)

# characteristic -> Characteristic: The characteristic for the buffer to read from
# (optional) timeout -> int = 1: How long we should wait for something new to read in seconds before giving up
# (optional) buffer_size -> int = 64: How much data the buffer can hold
def create_characteristic_buffer(characteristic: Characteristic, timeout: int = 1, buffer_size: int = 64) -> CharacteristicBuffer:
    properties = _convert_num_to_properties(characteristic.properties)
    
    # Check if it's possible to read from characteristic
    if properties[2]:
        return CharacteristicBuffer(characteristic, timeout=timeout, buffer_size=buffer_size)
    else:
        raise RoleError("ERROR: Cannot create buffer to read from characteristic when characteristic does not allow for reading!")

# characteristic -> Characteristic: The characteristic for the buffer to write to
# buffer_size -> int: The total size of the buffer
# max_packet_size -> int: The maximum size of how big a single write packet can be (should probably be around buffer_size)
def create_packet_buffer(characteristic: Characteristic, buffer_size: int, max_packet_size: int) -> PacketBuffer:
    properties = _convert_num_to_properties(characteristic.properties)
    
    # Check if it's possible to write to the characteristic
    if properties[0] or properties[1]:
        return PacketBuffer(characteristic, buffer_size=buffer_size, max_packet_size=max_packet_size)
    else:
        raise RoleError("ERROR: Cannot create buffer to write to a characteristic when characteristic does not allow for writing!")

def read_from_characteristic(read_buffer: CharacteristicBuffer) -> string:
    if get_bluetooth_connection_state():
        return read_buffer.readline().decode()
    else:
        raise Exception("ERROR: Not connected to another device!")

# write_buffer -> PacketBuffer: The buffer to write to
# message -> string: The message to send to the buffer
# (optional) max_length -> int = 20: The max length of a packet sent with the buffer
# (optional) clear_buffer -> bool = True: Whether or not to clear the buffer before sending the specified message
def write_to_characteristic(write_buffer: PacketBuffer, message: string, max_length: int = 20, clear_buffer: bool = True) -> int:
    if get_bluetooth_connection_state():
        if clear_buffer:
            # Clear the buffer then write the actual message to prevent old messages from bleeding over
            write_buffer.write(bytes((" " * (max_length - 1)) + "\n", 'utf-8'))
        return write_buffer.write(bytes(message, 'utf-8'))
    else:
        raise Exception("ERROR: Not connected to another device!")

#
# Peripheral Functions
#

def start_advertising(Advertisement):
    if not get_bluetooth_advertising_state() and bluetooth_mode_peripheral:
        _radio.start_advertising(ProvideServicesAdvertisement(service))
    elif not bluetooth_mode_peripheral:
        raise RoleError("ERROR: Device is not acting as peripheral! Cannot work with advertisements!")
    else:
        raise Exception("ERROR: Already advertising! Cannot begin new advertisement!")
    
def stop_advertising():
    if get_bluetooth_advertising_state():
        _radio.stop_advertising()
    else:
        raise Exception("ERROR: Not advertising! Cannot stop nonexistant advertisement!")

#
# Host Functions
#

# This function lets the user scan for advertisements with a variety of settings to adjust how we scan
# (optional) advertisements_to_collect -> int = 10: The total amount of advertisements we can collect in a scan
# (optional) buffer_size -> int = 512: How big a detected advertisement can be
# (optional) extended -> bool = False: When true it will support extended advertisement packets
# (optional) timeout -> float = None: The amount of time we should wait between detected advertisements to stop the scan
# (optional) interval -> float = 0.1: The interval (in seconds) between the start of two consecutive scan windows, must be in the range 0.0025 - 40.959375 seconds.
# (optional) window -> float = 0.1: How long to spend scanning a single BLE channel must be <= interval
# (optional) minimum_rssi -> int = -80: The minimum rssi an advertisement must have in order to be detected
# (optional) filter_no_name -> bool = True: If true it will filter out any advertisements that don't have a name
# (optional) active -> bool = True: Allows the scan to actually request and retrieve scan responses (not sure why you'd turn this off)
# (optional) print_debug -> bool = False: Prints debug information if true
def start_scanning(advertisements_to_collect: int = 10, buffer_size: int = 512, extended: bool = False, timeout: float = None, interval: float = 0.1, window: float = 0.1, minimum_rssi: int = -80, filter_no_name: bool = True, active: bool = True, print_debug: bool = False) -> dict:
    if not bluetooth_mode_peripheral:
        detected_devices = dict()
        amount_of_advertisements = 0
        try:
            for advertisement in _radio.start_scan(ProvideServicesAdvertisement, Advertisement, buffer_size=buffer_size, extended=extended, timeout=timeout, interval=interval, window=window, minimum_rssi=minimum_rssi, active=active):
            
                # If detected advertisements have a name and we don't have 50 or more collected then we should add it as that's
                # a device we can connect to without using up all our memory
                if (filter_no_name and advertisement.complete_name == None) or amount_of_advertisements >= advertisements_to_collect:
                    continue;
            
                # Increment to have an accurate amount of advertisements that passed the check
                amount_of_advertisements += 1
            
                # Print info about a detected device if we're about to add it
                if print_debug and ((not filter_no_name) + (detected_devices.get(advertisement.complete_name) == None)) >= 1:
                    print(advertisement.address, advertisement)
                    print("Short Name:", advertisement.short_name)
                    print("Full Name:", advertisement.complete_name)
                    print("Transmit Power:", advertisement.tx_power)
                    print("Appearance:", advertisement.appearance)
                    print("RSSI:", advertisement.rssi)
                    print(repr(advertisement) + "\n")
            
                # If the advertisement responds back it's likely a device and if we don't already have it we should add it
                if advertisement.scan_response and ((not filter_no_name) + (detected_devices.get(advertisement.complete_name) == None)) >= 1:
                    detected_devices[advertisement.complete_name] = advertisement.address
            
            if print_debug:
                print("Number of Collected Advertisements:", amount_of_advertisements)
        except MemoryError:
            raise MemoryError("Too much data! Change your scan settings to hold less data!")
        
        return detected_devices
    else:
        raise RoleError("ERROR: Device is not acting as Host! Cannot scan for advertisements!")

def stop_scanning():
    _radio.stop_scan()

# detected_devices must be a dictionary that has the device's name as a key with the device's address as it's value
def connect(detected_devices: dict, device_name: string, print_debug: bool = False) -> BLEConnection:
    if not bluetooth_mode_peripheral:
        try:
            ble = _radio.connect(detected_devices[device_name])
            
            if print_debug:
                print("Connected to ", device_name, ": ", detected_devices[device_name], ": ", get_bluetooth_connection_state(), sep="")
            
            return ble
        except KeyError:
            raise BluetoothError("Device name not found! Cannot connect to nonexistant device!")
    else:
        raise RoleError("ERROR: Device is not acting as Host! Cannot connect to another device!")

def disconnect(ble: BLEConnection, print_debug: bool = False):
    if not bluetooth_mode_peripheral:
        if ble != None and get_bluetooth_connection_state():
            ble.disconnect()
            
            if print_debug:
                print("Disconnected")
    else:
        raise RoleError("ERROR: Device is not acting as Host! Cannot disconnect from a device!")

# This allows for a host to work with services from a connected peripheral
def discover_device_services(ble: BLEConnection, filters: list = []) -> tuple:
    if not bluetooth_mode_peripheral:
        # Make sure our connections are good
        if ble and get_bluetooth_connection_state() and ble.connected:
            uuid_filters = []
            for entry in filters:
                uuid_filters.append(UUID(int(entry)))
                
            if len(uuid_filters) > 0:            
                return ble._bleio_connection.discover_remote_services(iter(uuid_filters))
            else:
                return ble._bleio_connection.discover_remote_services()
    else:
        raise RoleError("ERROR: Device is not acting as Host! Cannot discover services from connected device!")
#
# Miscellaneous Functions
#

# This converts from a boolean array of 6 in length into a number for characteristic properties
def _convert_properties_to_num(properties: list) -> int:
    num = 0
    for i in range(0, 6):
        if properties[i]:
            num += pow(2, abs(i - 5))
    return num

# This converts from a number to a boolean array of 6 in length for characteristic properties
def _convert_num_to_properties(num: int) -> list:
    properties = [False] * 6
    
    binary = bin(num)[2:8]
    binary = ("0" * (6 - len(binary))) + binary

    for i in range(0, 6):
        if binary[i] == '1':
            properties[i] = True
            
    return properties

#
# Variables
#

## This variable keeps track of whether we are in peripheral mode or host mode which
## allows for different features to become available. Host Mode allows for you to scan and connect to devices.
## Peripheral Mode allows you to advertise your own services and characteristics for a host to work with.
bluetooth_mode_peripheral = False

## This stores the previous bluetooth mode state when switching between states to keep proper track of them
bluetooth_mode_previous = False

## max_length is the length in bytes that a packet we will send will be
max_length = 20

## adder is a variable that counts up every frame and it's also what we send as a test value
adder = 0

## These are variables for the host to use when working with data from a peripheral
h_service = None
h_characteristic = None
h_read_buffer = None
h_write_buffer = None

## These are variables for a peripheral to advertisement with
p_service = create_service("0x185A")
p_characteristic = add_characteristic_to_service(p_service, "0x2BDE", properties=[True, False, True, True, False, True], max_length=max_length, fixed_length=True)
p_read_buffer = create_characteristic_buffer(p_characteristic)
p_write_buffer = create_packet_buffer(p_characteristic, buffer_size=max_length, max_packet_size=max_length)

## radio is a BLERadio which allows it to scan for devices and handle basic connections
_radio = BLERadio()

## ble will eventually become a BLEConnection which will then be able to be used to disconnect
ble = None

#
# Initalization
#

# This doesn't really do anything in this code but if I eventually get around to doing stuff with the neopixels on the board
# then it will stop me from being blinded as those things are really bright
cp.pixels.brightness = 0.1

# This just prints bluetooth information about the board like the name and the address of it
print("Device Name:", get_bluetooth_name())
print("Transmit Power:", get_bluetooth_transmission_power())
print("Address:", get_bluetooth_address())
print("Is Connected:", get_bluetooth_advertising_state())
print("Is Advertising:", get_bluetooth_advertising_state(), "\n")

#
# Main Loop
#
while True:
    # Set bluetooth mode based on the position of the slideswitch on the board
    bluetooth_mode_peripheral = not cp.switch
    
    # Make sure the bluetooth mode updates properly
    time.sleep(0.002)
    
    # Handle switching bluetooth mode by stopping any scanning, connections, or advertisements if we swap during them
    if bluetooth_mode_peripheral != bluetooth_mode_previous:
        if bluetooth_mode_peripheral:
            stop_scanning()
            if ble != None and ble.connected:
                disconnect(ble)
            
            print("Swapped to Peripheral Mode\n")
        else:
            if get_bluetooth_advertising_state():
                stop_advertising()
            
            print("Swapped to Host Mode\n")
    
    bluetooth_mode_previous = bluetooth_mode_peripheral
    
    try:
        # Very buggy and barely working code for reading and writing data to and from a characteristic
        if get_bluetooth_connection_state():
            if h_read_buffer != None:
                print(h_characteristic.value.decode())
                print(int.from_bytes(h_characteristic.value, "little"))
                #print(read_from_characteristic(h_read_buffer))
            if h_write_buffer != None:
                write_to_characteristic(h_write_buffer, str(adder) + "\n")
                #h_characteristic.value = bytes(str(adder), 'utf-8')
                #print(read_from_characteristic(read_buffer))
                #write_to_characteristic(write_buffer, str(adder))
            adder += 1
        else:
            if h_read_buffer != None:
                h_read_buffer = None
            if h_write_buffer != None:
                h_write_buffer = None
    except:
        print("ERROR: Something went wrong when working with data from another device!")

    # If we press button A then begin advertising and or connecting to a device
    if cp.button_a:
        # Make sure we aren't advertising and that we're in peripheral mode
        if not get_bluetooth_advertising_state() and bluetooth_mode_peripheral:
            # Begin advertising when the user wants them too
            start_advertising(ProvideServicesAdvertisement(p_service))
            print("Started Advertising")
        
        # Make sure we aren't connected to another device and that we're in host mode
        if not get_bluetooth_connection_state() and not bluetooth_mode_peripheral:
            
            # Catch if we have any memory related errors when scanning because we only have so much memory
            try:
                # Make sure we aren't already scanning
                stop_scanning()
                
                # Scan for devices with these arbitrary settings to make sure that we don't run out of memory
                detected_devices = start_scanning(buffer_size=50, timeout=1, print_debug = True)
                
                # print all the devices that we could connect to
                for key in detected_devices.keys():
                    print(key)
                    #print(detected_devices[key])
            except MemoryError:
                # If we have a memory error tell the user and stop attempting connection
                print("ERROR: Scanning Failed due to Memory Issues! (likely an overflow)\n")
                continue
            
            # Allow user to specify peripheral they want to connect to
            peripheral_name = None
            while peripheral_name == None:
                # Let the user input text
                temp_name = input("\nPlease type a peripheral name to connect to. (type 'exit' to cancel) (case sensitive)\n")
                
                # Check if the user wants to cancel action or provides a valid peripheral name
                if temp_name in detected_devices.keys():
                    peripheral_name = temp_name
                elif temp_name.lower() == "exit":
                    # Exit if user decides aganist connecting
                    print("Exiting scan...")
                    break
                else:
                    # If the user doesn't actually provide a valid peripheral name then make sure we make them 
                    print("\nPlease insert a valid peripheral name")
            
            # Attempt to connect to peripheral
            try:
                ble = connect(detected_devices, peripheral_name, True)
            except:
                print("\nERROR: could not find device name.\n")
                continue
                
            try:
                # Give us a little time to be connected
                time.sleep(0.1)
                
                # Find the services the peripheral offers
                h_services = discover_device_services(ble)
                
                # Get the service from the user
                while h_service == None:
                    service_uuids = ()
                    
                    # Get services with valid uuids and print them for the user
                    for i in range(0, len(h_services)):
                        if h_services[i].uuid != None:
                            print(h_services[i].uuid)
                            service_uuids += (h_services[i].uuid.uuid16,)
                    
                    # Let the user specify the uuid of the service they want to access
                    user_service = input("Please insert one of the hexadecimal values seen above to focus on the desired service (include 0x)\n")
                    
                    # Find the service the user specified
                    for i in range(0, len(service_uuids)):
                        if int(user_service) == service_uuids[i]:
                            h_service = h_services[i]
                            break
                
                # Get the first characteristic that allows us to read and or write to it
                for i in range(0, len(h_service.characteristics)):
                    # Get the properties to check what the characteristic will let us do
                    properties = _convert_num_to_properties(h_service.characteristics[i].properties)
                    
                    # Check if we can read from this characteristic and if so then store it
                    if properties[2] and h_characteristic == None:
                        h_characteristic = h_service.characteristics[i]
                        h_read_buffer = create_characteristic_buffer(h_characteristic)
                    
                    # Check if we can write to this characteristic and if so then store it
                    if (properties[0] or properties[1]) and h_characteristic == None:
                       h_write_buffer = create_packet_buffer(h_characteristic, buffer_size=max_length, max_packet_size=max_length)
                
                #h_characteristic.set_cccd(notify=True)
            except BluetoothError:
                # If we get a Bluetooth Error for whatever reason than tell the user something messed up
                print("ERROR: something went wrong when setting up data transfer with peripheral.")
                continue
            except ConnectionError:
                # If we get a Connection Error than handle it and tell the user something messed up
                print("ERROR: something went wrong when connecting to peripheral! Disconnecting...")
                if get_bluetooth_connection_state():
                    disconnect(ble)
                continue
                    
    # If we press button B then disconnect and or stop advertising
    if cp.button_b:
        # Check that we are advertising and that we are in peripheral mode and if so then stop advertising
        if get_bluetooth_advertising_state() and bluetooth_mode_peripheral:
            stop_advertising()
            print("Stopped Advertising")
        
        # Check if we are connected to a device and are in host mode and if so then disconnect
        if get_bluetooth_connection_state() and not bluetooth_mode_peripheral:
            disconnect(ble, True)