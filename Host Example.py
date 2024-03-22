#
# Libraries
#

import time
from adafruit_circuitplayground import cp
from ble_management import BluetoothManager
from _bleio import BluetoothError, RoleError
from adafruit_ble.advertising.standard import Advertisement, ProvideServicesAdvertisement

#
# Variables
#

# This is will allow us to interface with the ble_management library
ble_manager = BluetoothManager()

## adder is a variable that counts up every frame and it's also what we send as a test value
adder = 0

## These are variables for the host to use when working with data from a peripheral
h_service = None
h_characteristic = None

while True:
    try:
        # This code reads and writes to the current characteristic based on whether or not we are in host or peripheral mode
        if ble_manager.get_bluetooth_connection_state():
            # Get the properties of the characteristic
            properties = ble_manager.convert_num_to_properties(h_characteristic.properties)
            
            # Check to see if we can read from the characteristic
            if properties[2]:
                print(ble_manager.read_from_characteristic(h_characteristic).decode())
            
            # Check to see if we can write to the characteristic
            if properties[0] or properties[1]:
                ble_manager.write_to_characteristic(h_characteristic, str(adder) + "\n")         
            
            # Increment our test variable
            adder += 1
    except Exception as e:
        print("ERROR: Something went wrong when working with data from another device!\nException:", e, "\n")
    
    # If we press button A then begin connecting to a device
    if cp.button_a:
        # Make sure we aren't already connected to a device
        if not ble_manager.get_bluetooth_connection_state():
                # Catch if we have any memory related errors when scanning because we only have so much memory
                try:
                    # Make sure we aren't already scanning
                    ble_manager.stop_scanning()
                    
                    # Scan for devices with these arbitrary settings to make sure that we don't run out of memory
                    detected_devices = ble_manager.start_scanning(buffer_size=50, timeout=1, print_debug = True)
                    
                    # print all the devices that we could connect to
                    for key in detected_devices.keys():
                        print(key)

                except MemoryError as m:
                    # If we have a memory error tell the user and stop attempting connection
                    print("ERROR: Scanning Failed due to Memory Issues!\nException:", m, "\n")
                    continue
                
                # Allow user to specify peripheral they want to connect to
                is_exiting = False
                peripheral_name = None
                while peripheral_name == None:
                    # Let the user input text
                    temp_name = input("\nPlease type a peripheral name to connect to. (type 'exit' to cancel) (case sensitive)\n")
                    
                    # Check if the user wants to cancel action or provides a valid peripheral name
                    if temp_name in detected_devices.keys():
                        peripheral_name = temp_name
                    elif temp_name.lower() == "exit":
                        # Exit if user decides aganist connecting
                        is_exiting = True
                        print("\nExiting scan...\n")
                        break
                    else:
                        # If the user doesn't actually provide a valid peripheral name then make sure we make them 
                        print("\nPlease insert a valid peripheral name")
                
                # Attempt to connect to peripheral
                try:
                    ble_manager.connect(detected_devices, peripheral_name, True)
                except:
                    if not is_exiting:
                        print("\nERROR: could not find device name.\n")
                    continue
                    
                try:
                    # Give us a little time to be connected
                    time.sleep(0.1)
                    
                    # Find the services the peripheral offers
                    h_services = ble_manager.discover_device_services()
                    
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
                            
                    # Get the first useable characteristic in the service
                    for i in range(len(h_service.characteristics)):
                        properties = ble_manager.convert_num_to_properties(h_service.characteristics[i].properties)
                        
                        # Check if this characteristic exists and if so make it the one that we can use
                        if h_service.characteristics[i] != None and ((properties[0] or properties[1]) or properties[2]):
                            h_characteristic = h_service.characteristics[i]
                            break
                                            
                except BluetoothError as b:
                    # If we get a Bluetooth Error for whatever reason than tell the user something messed up
                    print("ERROR: something went wrong when setting up data transfer with peripheral.\nException:", b)
                    continue

                except ConnectionError as c:
                    # If we get a Connection Error than handle it and tell the user something messed up
                    print("ERROR: something went wrong when connecting to peripheral! Disconnecting...\nException:", c)
                    if ble_manager.get_bluetooth_connection_state():
                        disconnect()
                    continue

    # If we press button B then disconnect
    if cp.button_b:
        # Check if we are connected to a device and are in host mode and if so then disconnect
        if ble_manager.get_bluetooth_connection_state():
            ble_manager.disconnect(True)