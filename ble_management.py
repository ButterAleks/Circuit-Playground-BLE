#
# Libraries
#

from adafruit_ble import BLERadio, BLEConnection
from adafruit_ble.advertising.standard import Advertisement, ProvideServicesAdvertisement
from _bleio import UUID, Service, RoleError, Attribute, PacketBuffer, Characteristic, BluetoothError, CharacteristicBuffer


class BluetoothManager:
    #
    # Variables
    #
    
    ## This variable keeps track of whether we are in peripheral mode or host mode which
    ## allows for different features to become available. Host Mode allows for you to scan and connect to devices.
    ## Peripheral Mode allows you to advertise your own services and characteristics for a host to work with.
    bluetooth_mode_peripheral = False
    
    ## radio is a BLERadio which allows it to scan for devices and handle basic connections
    _radio = BLERadio()

    ## ble will eventually become a BLEConnection which will then be able to be used to disconnect
    ble = None
    
    #
    # Functions
    #
    
    def __init__(self):
        pass
    #
    # General Functions
    #

    # Set if we are acting as a host or a peripheral

    # Get our name for bluetooth
    def get_bluetooth_name(self) -> string:
        return self._radio.name

    # Get our transmission power
    def get_bluetooth_transmission_power(self) -> int:
        return self._radio.tx_power

    # Get our bluetooth address
    def get_bluetooth_address(self) -> bytes:
        return self._radio.address_bytes

    # Get our current state of advertising
    def get_bluetooth_advertising_state(self) -> bool:
        return self._radio.advertising

    # Get our current state of connection
    def get_bluetooth_connection_state(self) -> bool:
        return self._radio.connected

    # Create a service specified by it's UUID
    def create_service(self, uuid: string) -> Service:
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
    def add_characteristic_to_service(self, service: Service, uuid: string, properties: list = [False] * 6, read_perm: Attribute = Attribute.OPEN, write_perm: Attribute = Attribute.OPEN, max_length: int = 20, fixed_length: bool = False, user_description: string = None) -> Characteristic:
        return Characteristic.add_to_service(service, UUID(int(uuid)), properties=self._convert_properties_to_num(properties), read_perm=read_perm, write_perm=write_perm, max_length=max_length, fixed_length=fixed_length, user_description=user_description)

    # characteristic -> Characteristic: The characteristic for the buffer to read from
    # (optional) timeout -> int = 1: How long we should wait for something new to read in seconds before giving up
    # (optional) buffer_size -> int = 64: How much data the buffer can hold
    def create_characteristic_buffer(self, characteristic: Characteristic, timeout: int = 1, buffer_size: int = 64) -> CharacteristicBuffer:
        properties = self._convert_num_to_properties(characteristic.properties)
        
        # Check if it's possible to read from characteristic
        if properties[2]:
            return CharacteristicBuffer(characteristic, timeout=timeout, buffer_size=buffer_size)
        else:
            raise RoleError("ERROR: Cannot create buffer to read from characteristic when characteristic does not allow for reading!")

    # characteristic -> Characteristic: The characteristic for the buffer to write to
    # buffer_size -> int: The total size of the buffer
    # max_packet_size -> int: The maximum size of how big a single write packet can be (should probably be around buffer_size)
    def create_packet_buffer(self, characteristic: Characteristic, buffer_size: int, max_packet_size: int) -> PacketBuffer:
        properties = self._convert_num_to_properties(characteristic.properties)
        
        # Check if it's possible to write to the characteristic
        if properties[0] or properties[1]:
            return PacketBuffer(characteristic, buffer_size=buffer_size, max_packet_size=max_packet_size)
        else:
            raise RoleError("ERROR: Cannot create buffer to write to a characteristic when characteristic does not allow for writing!")

    # This reads with a characteristic buffer
    def read_from_characteristic_with_buffer(self, read_buffer: CharacteristicBuffer) -> bytes:
        if self.get_bluetooth_connection_state():
            return read_buffer.readline()
        else:
            raise Exception("ERROR: Something went wrong when reading from characteristic!")
        
    # This reads with the direct value from the characteristic
    def read_from_characteristic(self, characteristic: Characteristic) -> bytearray:
        if self.get_bluetooth_connection_state():
            return characteristic.value
        else:
            raise Exception("ERROR: Something went wrong when reading from characteristic!")

    # write_buffer -> PacketBuffer: The buffer to write to
    # message -> string: The message to send to the buffer
    # (optional) max_length -> int = 20: The max length of a packet sent with the buffer
    # (optional) clear_buffer -> bool = True: Whether or not to clear the buffer before sending the specified message
    def write_to_characteristic_with_buffer(self, write_buffer: PacketBuffer, message: string, max_length: int = 20, clear_buffer: bool = True) -> int:
        if self.get_bluetooth_connection_state():
            if clear_buffer:
                # Clear the buffer then write the actual message to prevent old messages from bleeding over
                write_buffer.write(bytes((" " * (max_length - 1)) + "\n", 'utf-8'))
            return write_buffer.write(bytes(message, 'utf-8'))
        else:
            raise Exception("ERROR: Something went wrong when writing to characteristic!")

    # characteristic -> Characteristic: The characteristic to directly write to
    # message -> string: The message to send to the buffer
    # (optional) max_length -> int = 20: The max length of a packet sent with the buffer
    # (optional) clear_buffer -> bool = True: Whether or not to clear the buffer before sending the specified message
    def write_to_characteristic(self, characteristic: Characteristic, message: string, max_length: int = 20, clear_buffer: bool = True) -> bytearray:
        if self.get_bluetooth_connection_state():
            if clear_buffer:
                # Clear the buffer then write the actual message to prevent old messages from bleeding over
                characteristic.value = bytes((" " * (max_length - 1)) + "\n", 'utf-8')
            characteristic.value = bytes(message, 'utf-8')
            
            return characteristic.value
        else:
            raise Exception("ERROR: Something went wrong when writing to characteristic!")

    #
    # Peripheral Functions
    #

    def start_advertising(self, advertisement: Advertisement):
        if not self.get_bluetooth_advertising_state() and self.bluetooth_mode_peripheral:
            self._radio.start_advertising(advertisement)
        elif not self.bluetooth_mode_peripheral:
            raise RoleError("ERROR: Device is not acting as peripheral! Cannot work with advertisements!")
        else:
            raise Exception("ERROR: Already advertising! Cannot begin new advertisement!")
        
    def stop_advertising(self):
        if self.get_bluetooth_advertising_state():
            self._radio.stop_advertising()
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
    def start_scanning(self, advertisements_to_collect: int = 10, buffer_size: int = 512, extended: bool = False, timeout: float = None, interval: float = 0.1, window: float = 0.1, minimum_rssi: int = -80, filter_no_name: bool = True, active: bool = True, print_debug: bool = False) -> dict:
        if not self.bluetooth_mode_peripheral:
            detected_devices = dict()
            amount_of_advertisements = 0
            
            for advertisement in self._radio.start_scan(ProvideServicesAdvertisement, Advertisement, buffer_size=buffer_size, extended=extended, timeout=timeout, interval=interval, window=window, minimum_rssi=minimum_rssi, active=active):
                
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
            
            return detected_devices
        else:
            raise RoleError("ERROR: Device is not acting as Host! Cannot scan for advertisements!")

    def stop_scanning(self):
        self._radio.stop_scan()

    # detected_devices must be a dictionary that has the device's name as a key with the device's address as it's value
    def connect(self, detected_devices: dict, device_name: string, print_debug: bool = False) -> BLEConnection:
        if not self.bluetooth_mode_peripheral:
            try:
                self.ble = self._radio.connect(detected_devices[device_name])
                
                if print_debug:
                    print("Connected to ", device_name, ": ", detected_devices[device_name], ": ", self.get_bluetooth_connection_state(), sep="")
                
                return self.ble
            except KeyError:
                raise BluetoothError("Device name not found! Cannot connect to nonexistant device!")
        else:
            raise RoleError("ERROR: Device is not acting as Host! Cannot connect to another device!")

    def disconnect(self, print_debug: bool = False):
        if not self.bluetooth_mode_peripheral:
            if self.ble != None and self.get_bluetooth_connection_state():
                self.ble.disconnect()
                
                if print_debug:
                    print("Disconnected")
        else:
            raise RoleError("ERROR: Device is not acting as Host! Cannot disconnect from a device!")

    # This allows for a host to work with services from a connected peripheral
    def discover_device_services(self, filters: list = []) -> tuple:
        if not self.bluetooth_mode_peripheral:
            # Make sure our connections are good
            if self.ble and self.get_bluetooth_connection_state() and self.ble.connected:
                uuid_filters = []
                for entry in filters:
                    uuid_filters.append(UUID(int(entry)))
                    
                if len(uuid_filters) > 0:            
                    return self.ble._bleio_connection.discover_remote_services(iter(uuid_filters))
                else:
                    return self.ble._bleio_connection.discover_remote_services()
        else:
            raise RoleError("ERROR: Device is not acting as Host! Cannot discover services from connected device!")
    #
    # Miscellaneous Functions
    #

    # This converts from a boolean array of 6 in length into a number for characteristic properties
    def _convert_properties_to_num(self, properties: list) -> int:
        num = 0
        for i in range(0, 6):
            if properties[i]:
                num += pow(2, abs(i - 5))
        return num

    # This converts from a number to a boolean array of 6 in length for characteristic properties
    def _convert_num_to_properties(self, num: int) -> list:
        properties = [False] * 6
        
        binary = bin(num)[2:8]
        binary = ("0" * (6 - len(binary))) + binary

        for i in range(0, 6):
            if binary[i] == '1':
                properties[i] = True
                
        return properties