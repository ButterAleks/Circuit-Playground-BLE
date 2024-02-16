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

ble_manager = BluetoothManager()

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
p_service = ble_manager.create_service("0x185A")
p_characteristic = ble_manager.add_characteristic_to_service(p_service, "0x2BDE", properties=[True, False, True, True, False, True], max_length=max_length)
p_read_buffer = ble_manager.create_characteristic_buffer(p_characteristic)
p_write_buffer = ble_manager.create_packet_buffer(p_characteristic, buffer_size=max_length, max_packet_size=max_length)

#
# Initalization
#

# This doesn't really do anything in this code but if I eventually get around to doing stuff with the neopixels on the board
# then it will stop me from being blinded as those things are really bright
cp.pixels.brightness = 0.1

# This just prints bluetooth information about the board like the name and the address of it
print("Device Name:", ble_manager.get_bluetooth_name())
print("Transmit Power:", ble_manager.get_bluetooth_transmission_power())
print("Address:", ble_manager.get_bluetooth_address())
print("Is Connected:", ble_manager.get_bluetooth_connection_state())
print("Is Advertising:", ble_manager.get_bluetooth_advertising_state(), "\n")

#
# Main Loop
#
while True:
    # Set bluetooth mode based on the position of the slideswitch on the board
    ble_manager.bluetooth_mode_peripheral = not cp.switch
    
    # Make sure the bluetooth mode updates properly
    time.sleep(0.002)
    
    try:
        # Handle switching bluetooth mode by stopping any scanning, connections, or advertisements if we swap during them
        if ble_manager.bluetooth_mode_peripheral != bluetooth_mode_previous:
            if ble_manager.bluetooth_mode_peripheral:
                ble_manager.stop_scanning()
                if ble_manager.ble != None and ble_manager.get_bluetooth_connection_state():
                    ble_manager.disconnect()
                
                print("Swapped to Peripheral Mode\n")
            else:
                if ble_manager.get_bluetooth_advertising_state():
                    ble_manager.stop_advertising()
                
                print("Swapped to Host Mode\n")
        
        bluetooth_mode_previous = ble_manager.bluetooth_mode_peripheral
    except Exception as e:
        print("ERROR: Something went wrong when switching Bluetooth Mode!\nException:", e, "\n")
     
    try:
        # Got this code working better now after making a lot of mistakes with it
        if ble_manager.get_bluetooth_connection_state():
            if h_read_buffer != None:
                print(ble_manager.read_from_characteristic(h_characteristic).decode())
                #print(read_from_characteristic_with_buffer(h_read_buffer).decode())
            if h_write_buffer != None:
                ble_manager.write_to_characteristic(h_characteristic, str(adder) + "\n")
                #write_to_characteristic_with_buffer(h_write_buffer, str(adder) + "\n")
            
            if p_read_buffer != None:
                #print(read_from_characteristic(p_characteristic).decode())
                print(ble_manager.read_from_characteristic_with_buffer(p_read_buffer).decode())
            if p_write_buffer != None:
                #write_to_characteristic(p_characteristic, str(adder) + "\n")
                ble_manager.write_to_characteristic_with_buffer(p_write_buffer, str(adder) + "\n")
                
            adder += 1
        else:
            if h_read_buffer != None:
                h_read_buffer = None
            if h_write_buffer != None:
                h_write_buffer = None
    except Exception as e:
        print("ERROR: Something went wrong when working with data from another device!\nException:", e, "\n")

    # If we press button A then begin advertising and or connecting to a device
    if cp.button_a:
        # Make sure we aren't advertising and that we're in peripheral mode
        if not ble_manager.get_bluetooth_advertising_state() and ble_manager.bluetooth_mode_peripheral:
            # Begin advertising when the user wants them too
            ble_manager.start_advertising(ProvideServicesAdvertisement(p_service))
            print("Started Advertising")
        
        # Make sure we aren't connected to another device and that we're in host mode
        if not ble_manager.get_bluetooth_connection_state() and not ble_manager.bluetooth_mode_peripheral:
            
            # Catch if we have any memory related errors when scanning because we only have so much memory
            try:
                # Make sure we aren't already scanning
                ble_manager.stop_scanning()
                
                # Scan for devices with these arbitrary settings to make sure that we don't run out of memory
                detected_devices = ble_manager.start_scanning(buffer_size=50, timeout=1, print_debug = True)
                
                # print all the devices that we could connect to
                for key in detected_devices.keys():
                    print(key)
                    #print(detected_devices[key])
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
                        
                # Get the first characteristic that allows us to read and or write to it
                for i in range(len(h_service.characteristics)):
                    # Get the properties to check what the characteristic will let us do
                    properties = ble_manager._convert_num_to_properties(h_service.characteristics[i].properties)
                    
                    # Check if we can read from this characteristic and if so then store it
                    if properties[2] and h_service.characteristics[i] != None:
                        h_characteristic = h_service.characteristics[i]
                        h_read_buffer = ble_manager.create_characteristic_buffer(h_characteristic)
                    
                    # Check if we can write to this characteristic and if so then store it
                    if (properties[0] or properties[1]) and h_service.characteristics[i] != None:
                        h_write_buffer = ble_manager.create_packet_buffer(h_service.characteristics[i], buffer_size=max_length, max_packet_size=max_length)
                
                #h_characteristic.set_cccd(notify=True)
            except BluetoothError as b:
                # If we get a Bluetooth Error for whatever reason than tell the user something messed up
                print("ERROR: something went wrong when setting up data transfer with peripheral.\nException:", b)
                continue
            except ConnectionError as c:
                # If we get a Connection Error than handle it and tell the user something messed up
                print("ERROR: something went wrong when connecting to peripheral! Disconnecting...\nException:", c)
                if get_bluetooth_connection_state():
                    disconnect()
                continue
                    
    # If we press button B then disconnect and or stop advertising
    if cp.button_b:
        # Check that we are advertising and that we are in peripheral mode and if so then stop advertising
        if ble_manager.get_bluetooth_advertising_state() and ble_manager.bluetooth_mode_peripheral:
            ble_manager.stop_advertising()
            print("Stopped Advertising")
        
        # Check if we are connected to a device and are in host mode and if so then disconnect
        if ble_manager.get_bluetooth_connection_state() and not ble_manager.bluetooth_mode_peripheral:
            ble_manager.disconnect(True)