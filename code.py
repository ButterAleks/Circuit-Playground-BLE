#
# Libraries
#

import time
import board
import digitalio
from adafruit_ble import BLERadio
from adafruit_ble import BLEConnection
from adafruit_circuitplayground import cp
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

#
# Functions
#



#
# Variables
#

## ble will eventually become a BLEConnection which will then be able to be used to disconnect
ble = None

## radio is a BLERadio which allows it to scan for devices and handle basic connections
radio = BLERadio()

## detected_devices will contain the addresses of devices that actually respond back when being found
detected_devices = dict()

## This tracks the total amount of advertisements being collected so that way we can stop the loop from accumulating
## too many devices so that way we don't run out of memory
amount_of_advertisements = 0

#
# Initalization
#

# This doesn't really do anything in this code but if I eventually get around to doing stuff with the neopixels on the board
# then it will stop me from being blinded as those things are really bright
cp.pixels.brightness = 0.1

# This just prints bluetooth information about the board like the name and the address of it
print("Device Name:", radio.name)
print("Transmit Power:", radio.tx_power)
print("Address:", radio.address_bytes)
print("Is Advertising:", radio.advertising)

# Tell the user that we're scanning
print("\nScanning\n")

# Stop any scan that might stop us from performing a new scan
radio.stop_scan()

# Start a scan that scans for regular advertisements or service advertisements with a small buffer size so we
# don't run out of memory and decently small timeout so we can exit quickly while making sure we get everything
for advertisement in radio.start_scan(ProvideServicesAdvertisement, Advertisement, buffer_size=50, timeout=10):
    
    # If detected advertisements have a name and we don't have 50 or more collected then we should add it as that's
    # a device we can connect to without using up all our memory
    if advertisement.complete_name == None or amount_of_advertisements >= 50:
        continue;
    
    # Increment to have an accurate amount of advertisements that passed the check
    amount_of_advertisements += 1
    
    # Print info about a detected device if we're about to add it
    if detected_devices.get(advertisement.complete_name) == None:
        print(advertisement.address, advertisement)
        print("Short Name:", advertisement.short_name)
        print("Full Name:", advertisement.complete_name)
        print("Transmit Power:", advertisement.tx_power)
        print("Appearance:", advertisement.appearance)
        print("RSSI:", advertisement.rssi)
        print(repr(advertisement) + "\n")
    
    # If the advertisement responds back it's likely a device and if we don't already have it we should add it
    if advertisement.scan_response and detected_devices.get(advertisement.complete_name) == None:
        detected_devices[advertisement.complete_name] = advertisement.address

# Prints the amount of recieved advertisements and also says that scanning is complete
print("Number of Collected Advertisements:", amount_of_advertisements)
print("Scanning Complete")

#
# Main Loop
#
while True:
    
    # If we press button A then connect and log what we connected too
    # (in this hardcoded case test since my test peripheral was named Test)
    if cp.button_a:
        # We also set ble because radio.connect returns a BLEConnection that we can use to disconnect from
        ble = radio.connect(detected_devices["Test"])
        print("Connected to Test:", detected_devices["Test"], ":", radio.connected)
    
    # If we press button B then disconnect and log that we did that
    if cp.button_b:
        if ble != None:
            ble.disconnect()
            print("Disconnected:", not radio.connected)