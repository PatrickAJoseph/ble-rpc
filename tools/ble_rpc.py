import asyncio
import sys
import time
import yaml
import ast

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

RPC_COMMAND_UUID = "e001"
RPC_RESPONSE_UUID = "e002"
RPC_NOTIFICATION_UUID = "e003"

RPC_MAX_PAYLOAD_LENGTH = 200
RPC_MAX_PACKET_LENGTH = RPC_MAX_PAYLOAD_LENGTH + 2

RPC_RESPONSE_TIMEOUT = 2.0
BLE_CONNECT_TIMEOUT = 15.0

class RPC:

    class RPC_request_parameter_value: 
        def __init__(self, command, command_id, parameter_name, parameter_type, is_a_list):
            self.name = command + ':request:' + parameter_name
            self.value: str = ''
            self.parameter_type:str = parameter_type
            self.is_a_list = is_a_list
            self.command_id = command_id
        
        def set(self, value):
            self.value = str(value)
        
        def get(self):
            return str(self.value)
        
        def print(self):
            print(f"Request parameter name: {self.name}")
            print(f"Request parameter value: {self.value}")
            print(f"Request parameter type: {self.parameter_type}")
            print(f"Request parameter is a list: {self.is_a_list}")
            print(f"Request parameter command id: {self.command_id}")

    class RPC_response_parameter_value: 
        def __init__(self, response, response_id, parameter_name, parameter_type, is_a_list, size_parameter: str = ''):
            self.name = response + ':response:' + parameter_name
            self.response_name = response
            self.response_parameter_name = parameter_name
            self.value: str = ''
            self.parameter_type:str = parameter_type
            self.is_a_list = is_a_list
            self.response_id = response_id
            self.size_parameter = size_parameter 
        
        def set(self, value):
            self.value = str(value)
        
        def get(self):
            return str(self.value)

        def print(self):
            print(f"Response parameter name: {self.name}")
            print(f"Response parameter value: {self.value}")
            print(f"Response parameter type: {self.parameter_type}")
            print(f"Response parameter is a list: {self.is_a_list}")
            print(f"Response parameter response id: {self.response_id}")
            print(f"Response parameter size parameter: {self.size_parameter}")

    class RPC_notification_parameter_value: 
        def __init__(self, notification, notification_id, parameter_name, parameter_type, is_a_list, size_parameter: str = ''):
            self.name = notification + ':notification:' + parameter_name
            self.value: str = ''
            self.parameter_type:str = parameter_type
            self.is_a_list = is_a_list
            self.notification_id = notification_id
            self.size_parameter = size_parameter
        
        def set(self, value):
            self.value = str(value)
        
        def get(self):
            return str(self.value)

        def print(self):
            print(f"Notification parameter name: {self.name}")
            print(f"Notification parameter value: {self.value}")
            print(f"Notification parameter type: {self.parameter_type}")
            print(f"Notification parameter is a list: {self.is_a_list}")
            print(f"Notification parameter notification id: {self.notification_id}")
            print(f"Notification parameter size parameter: {self.size_parameter}")
            
    def read_rpc_parameters(self):
        
        file_handle = open(self.rpc_file, 'r')
        
        yaml_data = yaml.safe_load(file_handle)

        commands = yaml_data['commands']
        
        for command in commands:
            
            request_parameters = command['request_parameters']
            response_parameters = command['response_parameters']
            
            for request_parameter in request_parameters:
                parameter = self.RPC_request_parameter_value(command['name'],
                                                        int(command['id']),
                                                        request_parameter['name'],
                                                        request_parameter['type'],
                                                        request_parameter['is_a_list'])
                self.rpc_request_parameters.append(parameter)

            for response_parameter in response_parameters:
                if response_parameter['is_a_list']:
                    parameter = self.RPC_response_parameter_value(command['name'],
                                                            int(command['id']),
                                                            response_parameter['name'],
                                                            response_parameter['type'],
                                                            response_parameter['is_a_list'],
                                                            response_parameter['size_parameter'])
                else:
                    parameter = self.RPC_response_parameter_value(command['name'],
                                                            int(command['id']),
                                                            response_parameter['name'],
                                                            response_parameter['type'],
                                                            response_parameter['is_a_list'])                
                self.rpc_response_parameters.append(parameter)

        notifications = yaml_data['notifications']
        
        for notification in notifications:
            
            notification_parameters = notification['notification_parameters']
            
            for notification_parameter in notification_parameters:
                if notification_parameter['is_a_list']:
                    parameter = self.RPC_notification_parameter_value(notification['name'],
                                                            int(notification['id']),
                                                            notification_parameter['name'],
                                                            notification_parameter['type'],
                                                            notification_parameter['is_a_list'],
                                                            notification_parameter['size_parameter'])
                else:
                    parameter = self.RPC_notification_parameter_value(notification['name'],
                                                            int(notification['id']),
                                                            notification_parameter['name'],
                                                            notification_parameter['type'],
                                                            notification_parameter['is_a_list'])                
                self.rpc_notification_parameters.append(parameter)

    def set_rpc_request_parameter_value(self, command_name, parameter_name, value):
        
        full_name = command_name + ":request:" + parameter_name
        
        request_parameter = None
        
        for entry in self.rpc_request_parameters:
            if entry.name == full_name:
                request_parameter = entry                

        if request_parameter.is_a_list == False:
            if request_parameter.parameter_type == 'uint8' or request_parameter.parameter_type == 'int8':        
                request_parameter.value = str( int(value) & 255 )
            
            if request_parameter.parameter_type == 'uint16' or request_parameter.parameter_type == 'int16':
                request_parameter.value = str( int(value) & (( 1 << 16) - 1) )

            if request_parameter.parameter_type == 'uint32' or request_parameter.parameter_type == 'int32':
                request_parameter.value = str( int(value) & (( 1 << 32) - 1) )

            if request_parameter.parameter_type == 'bool' or request_parameter.parameter_type == 'BOOL':
                request_parameter.value = str(value)

            if request_parameter.parameter_type == 'float':
                request_parameter.value = str(value)
        else:
            
            length = len(value)
            
            str_value = '['
            
            for _value in value:
                if request_parameter.parameter_type == 'uint8' or request_parameter.parameter_type == 'int8':        
                    str_value += str( int(_value) & 255 ) + ','

                if request_parameter.parameter_type == 'uint16' or request_parameter.parameter_type == 'int16':
                    str_value += str( int(_value) & (( 1 << 16) - 1) ) + ','

                if request_parameter.parameter_type == 'uint32' or request_parameter.parameter_type == 'int32':
                    str_value += str( int(_value) & (( 1 << 32) - 1) ) + ','

                if request_parameter.parameter_type == 'bool' or request_parameter.parameter_type == 'BOOL':
                    str_value += str(_value) + ','

                if request_parameter.parameter_type == 'float':
                    str_value += str(_value) + ','
            
            str_value = str_value[:len(str_value) - 1]    
            str_value += ']'
            
            request_parameter.value = str_value               

    def get_rpc_request_parameter_value(self, command_name, parameter_name):
        
        full_name = command_name + ':request:' + parameter_name
        
        _parameter = None
        
        for request_parameter in self.rpc_request_parameters:
            
            if request_parameter.name == full_name:
                _parameter = request_parameter
        
        return ast.literal_eval(_parameter.value)

    def set_rpc_response_parameter_value(self, command_name, parameter_name, value):
        
        full_name = command_name + ":response:" + parameter_name
        
        response_parameter = None
        
        for entry in self.rpc_response_parameters:
            if entry.name == full_name:
                response_parameter = entry                

        if response_parameter.is_a_list == False:
            if response_parameter.parameter_type == 'uint8' or response_parameter.parameter_type == 'int8':        
                response_parameter.value = str( int(value) & 255 )
            
            if response_parameter.parameter_type == 'uint16' or response_parameter.parameter_type == 'int16':
                response_parameter.value = str( int(value) & (( 1 << 16) - 1) )

            if response_parameter.parameter_type == 'uint32' or response_parameter.parameter_type == 'int32':
                response_parameter.value = str( int(value) & (( 1 << 32) - 1) )

            if response_parameter.parameter_type == 'bool' or response_parameter.parameter_type == 'BOOL':
                response_parameter.value = str(value)

            if response_parameter.parameter_type == 'float':
                response_parameter.value = str(value)
        else:
            
            length = len(value)
            
            str_value = '['
            
            for _value in value:
                if response_parameter.parameter_type == 'uint8' or response_parameter.parameter_type == 'int8':        
                    str_value += str( int(_value) & 255 ) + ','

                if response_parameter.parameter_type == 'uint16' or response_parameter.parameter_type == 'int16':
                    str_value += str( int(_value) & (( 1 << 16) - 1) ) + ','

                if response_parameter.parameter_type == 'uint32' or response_parameter.parameter_type == 'int32':
                    str_value += str( int(_value) & (( 1 << 32) - 1) ) + ','

                if response_parameter.parameter_type == 'bool' or response_parameter.parameter_type == 'BOOL':
                    str_value += str(_value) + ','

                if response_parameter.parameter_type == 'float':
                    str_value += str(_value) + ','
            
            str_value = str_value[:len(str_value) - 1]    
            str_value += ']'
            
            response_parameter.value = str_value               

    def get_rpc_response_parameter_value(self, command_name, parameter_name):
        
        full_name = command_name + ':response:' + parameter_name
        
        _parameter = None
        
        for response_parameter in self.rpc_response_parameters:
            
            if response_parameter.name == full_name:
                _parameter = response_parameter
        
        return ast.literal_eval(_parameter.value)

    def get_rpc_response_parameter_reference(self, command_name, parameter_name):
        
        full_name = command_name + ':response:' + parameter_name
        
        _parameter = None
        
        for response_parameter in self.rpc_response_parameters:
            
            if response_parameter.name == full_name:
                _parameter = response_parameter
        
        return _parameter


    def set_rpc_notification_parameter_value(self, notification_name, parameter_name, value):
        
        full_name = notification_name + ":notification:" + parameter_name
        
        notification_parameter = None
        
        for entry in self.rpc_notification_parameters:
            if entry.name == full_name:
                notification_parameter = entry                

        if notification_parameter.is_a_list == False:
            if notification_parameter.parameter_type == 'uint8' or notification_parameter.parameter_type == 'int8':        
                notification_parameter.value = str( int(value) & 255 )
            
            if notification_parameter.parameter_type == 'uint16' or notification_parameter.parameter_type == 'int16':
                notification_parameter.value = str( int(value) & (( 1 << 16) - 1) )

            if notification_parameter.parameter_type == 'uint32' or notification_parameter.parameter_type == 'int32':
                notification_parameter.value = str( int(value) & (( 1 << 32) - 1) )

            if notification_parameter.parameter_type == 'bool' or notification_parameter.parameter_type == 'BOOL':
                notification_parameter.value = str(value)

            if notification_parameter.parameter_type == 'float':
                notification_parameter.value = str(value)
        else:
            
            length = len(value)
            
            str_value = '['
            
            for _value in value:
                if notification_parameter.parameter_type == 'uint8' or notification_parameter.parameter_type == 'int8':        
                    str_value += str( int(_value) & 255 ) + ','

                if notification_parameter.parameter_type == 'uint16' or notification_parameter.parameter_type == 'int16':
                    str_value += str( int(_value) & (( 1 << 16) - 1) ) + ','

                if notification_parameter.parameter_type == 'uint32' or notification_parameter.parameter_type == 'int32':
                    str_value += str( int(_value) & (( 1 << 32) - 1) ) + ','

                if notification_parameter.parameter_type == 'bool' or notification_parameter.parameter_type == 'BOOL':
                    str_value += str(_value) + ','

                if notification_parameter.parameter_type == 'float':
                    str_value += str(_value) + ','
            
            str_value = str_value[:len(str_value) - 1]    
            str_value += ']'
            
            notification_parameter.value = str_value               

    def get_rpc_notification_parameter_value(self, notification_name, parameter_name):
        
        full_name = notification_name + ':notification:' + parameter_name
        
        _parameter = None
        
        for notification_parameter in self.rpc_notification_parameters:
            
            if notification_parameter.name == full_name:
                _parameter = notification_parameter
        
        return ast.literal_eval(_parameter.value)

    def form_command_packet(self, command_name: str):
        
        command_parameters = []
        
        packet = []
        
        for parameter in self.rpc_request_parameters:
            
            if command_name in parameter.name:
                command_parameters.append(parameter)

        for parameter in command_parameters:
            
            if parameter.is_a_list == False:
                
                if parameter.parameter_type == 'uint8' or parameter.parameter_type == 'int8':
                    _value = int(parameter.value)
                    packet.append(_value & 255)
                
                if parameter.parameter_type == 'uint16' or parameter.parameter_type == 'int16':
                    _value = int(parameter.value)
                    packet.append((_value >> 8) & 255)
                    packet.append(_value & 255)
                
                if parameter.parameter_type == 'uint32' or parameter.parameter_type == 'int32':
                    _value = int(parameter.value)
                    packet.append( ( _value >> 24 ) & 255 )
                    packet.append( ( _value >> 16 ) & 255 )
                    packet.append( ( _value >> 8 ) & 255 )
                    packet.append( _value & 255 )

                if parameter.parameter_type == 'BOOL' or parameter.parameter_type == 'bool':
                    _value = bool(parameter.parameter_value)
                    packet.append(_value)
            
            else:
            
                list_of_values = ast.literal_eval(parameter.parameter_value)

                for value in list_of_values:
                
                    if parameter.parameter_type == 'uint8' or parameter.parameter_type == 'int8':
                        _value = int(value)
                        packet.append(_value & 255)
                    
                    if parameter.parameter_type == 'uint16' or parameter.parameter_type == 'int16':
                        _value = int(value)
                        packet.append((_value >> 8) & 255)
                        packet.append(_value & 255)
                    
                    if parameter.parameter_type == 'uint32' or parameter.parameter_type == 'int32':
                        _value = int(value)
                        packet.append( ( _value >> 24 ) & 255 )
                        packet.append( ( _value >> 16 ) & 255 )
                        packet.append( ( _value >> 8 ) & 255 )
                        packet.append( _value & 255 )

                    if parameter.parameter_type == 'BOOL' or parameter.parameter_type == 'bool':
                        _value = bool(value)
                        packet.append(_value)

        packet = [command_parameters[0].command_id, len(packet)] + packet
        
        return bytes(packet)

    def disassemble_response_packet(self, packet: bytes):
        
        command_name: str = ''
        
        command_id = int(packet[0])
        command_length = int(packet[1])
        
        response_parameters = []
        
        packet = packet[2:]
        
        index = 0
        
        for parameter in self.rpc_response_parameters:
            
            if command_id == parameter.response_id:
            
                response_parameters.append(parameter)
                
        for parameter in response_parameters:
        
            if parameter.is_a_list == False:
                
                if parameter.parameter_type == 'uint8' or parameter.parameter_type == 'int8':
                   
                    _value = int(packet[index])
                    index += 1
                    
                    parameter.set(_value)
                
                if parameter.parameter_type == 'bool' or parameter.parameter_type == 'BOOL':
                   
                    _value = int(packet[index])
                    index += 1
                    
                    parameter.set(_value)                
                
                if parameter.parameter_type == 'uint16' or parameter.parameter_type == 'int16':
                
                    _value = int( int(packet[index] << 8) | int(packet[index + 1]) )
                    index += 2
                    
                    parameter.set(_value)
                    
                if parameter.parameter_type == 'uint32' or parameter.parameter_type == 'int32':

                    _value = int( int( packet[index] << 24 ) | int( packet[index+1] << 16 ) | int( packet[index+2] << 8 ) | int(packet[index+3]) )                
                    index += 4
                    
                    parameter.set(_value)

            else:
            
                list_length = int((self.get_rpc_response_parameter_reference( parameter.response_name + ":" + "response" + ":" + parameter.size_parameter )).get())

                values = []
                
                for x in range(0, list_length):

                    if parameter.parameter_type == 'uint8' or parameter.parameter_type == 'int8':
                       
                        _value = int(packet[index])
                        index += 1
                                            
                    if parameter.parameter_type == 'bool' or parameter.parameter_type == 'BOOL':
                       
                        _value = int(packet[index])
                        index += 1
                                            
                    if parameter.parameter_type == 'uint16' or parameter.parameter_type == 'int16':
                    
                        _value = int( int(packet[index] << 8) | int(packet[index + 1]) )
                        index += 2
                                                
                    if parameter.parameter_type == 'uint32' or parameter.parameter_type == 'int32':

                        _value = int( int( packet[index] << 24 ) | int( packet[index+1] << 16 ) | int( packet[index+2] << 8 ) | int(packet[index+3]) )                
                        index += 4
                    
                    values.append(_value)
                
                parameter.set(values)
                

    def __init__(self, device_name: str, rpc_file: str):
        self.device_name = device_name
        self.rpc_file: str = rpc_file

        self.rpc_request_parameters = []
        self.rpc_response_parameters = []
        self.rpc_notification_parameters = []

        self.read_rpc_parameters()

        self.ble_device: BLEDevice | None = None
        self.client: BleakClient | None = None

        self.command_uuid = RPC_COMMAND_UUID
        self.response_uuid = RPC_RESPONSE_UUID
        self.notification_uuid = RPC_NOTIFICATION_UUID

        # Future representing the response to the currently outstanding RPC.
        self.response_future: asyncio.Future[bytes] | None = None

        # Prevent multiple commands from using the same response Future.
        self.command_lock = asyncio.Lock()

        # Number of responses received.
        self.response_count = 0

        # Number of asynchronous notifications received.
        self.notification_count = 0

        self.command_uuid: str = ''
        self.response_uuid: str = ''
        self.notification_uuid: str = ''

    # Response handler
    # Once the device has written the response into the response characteristics
    # it sends out a notification to indicate to the host device that it has responded
    # to the command issued by the host.

    def response_handler(self, sender, data: bytearray):

        response = bytes(data)

        self.response_count += 1

        # Basic packet validation.
        if len(response) < 2:
            raise IOError("[Response] ERROR: response packet too short")
            return

        response_id = response[0]
        payload_length = response[1]

        if payload_length != len(response) - 2:
            raise IOError( f"[Response] ERROR: length mismatch: header={payload_length}, actual={len(response) - 2}" )
            return

        payload = response[2:]

        print( f"[Response] ID=0x{response_id:02X}, Length={payload_length}, Payload={payload.hex(' ')}" )

        if self.response_future is not None:
            if self.response_future.done():
                print("[Response] WARNING: response future already completed")
                return

            # Store the complete RPC response.
            self.response_future.set_result(response)

    # Notifications are sent by the device to the host without the host prompting
    # for a response from the device.

    def notification_handler(self, sender, data: bytearray):

        notification = bytes(data)

        self.notification_count += 1

        print( f"[Notification] Notification received: {notification.hex(' ')}" )

        if len(notification) < 2:
            raise IOError("[Notification] ERROR: notification packet too short")
            return

        notification_id = notification[0]
        payload_length = notification[1]

        if payload_length != len(notification) - 2:
            raise IOError( f"[Response] ERROR: length mismatch: header={payload_length}, actual={len(notification) - 2}" )
            return

        payload = notification[2:]

        print(
            f"[E003] ID=0x{notification_id:02X}, "
            f"Length={payload_length}, "
            f"Payload={payload.hex(' ')}"
        )

    #
    # Scan through available devices and connect with target device.
    #

    async def get_device(self):
        print(f"Searching for device: {self.device_name}")

        devices = await BleakScanner.discover(timeout=10.0)

        for device in devices:

            print( f"Found device: {device.name} | {device.address}" )

            if device.name == self.device_name:

                self.ble_device = device

                print()
                print("Target device found !")
                print(f"Device name: {device.name} | Address: {device.address}")

                return

        raise IOError(f"Target device '{self.device_name}' not found")

    #
    #   Connect with target device.
    #

    async def connect(self):

        if self.ble_device is None:
            await self.get_device()

        print()
        print("Connecting with server ...")

        self.client = BleakClient(self.ble_device)

        try:
            await asyncio.wait_for( self.client.connect(), timeout=BLE_CONNECT_TIMEOUT )

        except Exception as exc:
            raise IOError( f"Unable to connect to BLE device: {exc}" ) from exc

        print(f"Connected with {self.ble_device.name} at address {self.ble_device.address}")

        #
        # Scan through the available services and search for characteristics with UUIDs
        # for command, response and notifications.
        #

        services = self.client.services

        print()
        print("BLE services/characteristics:")

        for service in services:

            print(f"\nService: {service.uuid}")

            for characteristic in service.characteristics:
                print(f"  Characteristic UUID: {characteristic.uuid}")
                print(f"  Description: {characteristic.description}")
                
                if RPC_COMMAND_UUID in characteristic.uuid:
                    self.command_uuid = characteristic.uuid
                    print(f"RPC command UUID: {self.command_uuid}")
                
                if RPC_RESPONSE_UUID in characteristic.uuid:
                    self.response_uuid = characteristic.uuid
                    print(f"RPC response UUID: {self.response_uuid}")
                
                if RPC_NOTIFICATION_UUID in characteristic.uuid:
                    self.notification_uuid = characteristic.uuid
                    print(f"RPC notification UUID: {self.notification_uuid}")

        print()
        print("RPC characteristics found:")
        print(f"  Command      : {self.command_uuid}")
        print(f"  Response     : {self.response_uuid}")
        print(f"  Notification : {self.notification_uuid}")

        print()
        print("Enabling RPC response notifications...")

        await self.client.start_notify( self.response_uuid, self.response_handler )

        print("RPC response notifications enabled.")
        print("Enabling RPC asynchronous notifications...")

        await self.client.start_notify( self.notification_uuid, self.notification_handler )

        print("RPC asynchronous notifications enabled.")

    # ------------------------------------------------------------------------
    # Characteristic lookup
    # ------------------------------------------------------------------------

    def _find_characteristic(self, uuid: str) -> bool:

        if self.client is None:
            return False

        target_uuid = uuid.lower()

        for service in self.client.services:

            for characteristic in service.characteristics:

                if characteristic.uuid.lower() == target_uuid:
                    return True

        return False

    # ------------------------------------------------------------------------
    # Send RPC command and wait for response
    # ------------------------------------------------------------------------

    async def send_command( self, command: bytes, timeout: float = RPC_RESPONSE_TIMEOUT ) -> bytes:

        if self.client is None or not self.client.is_connected:
            raise IOError("BLE client is not connected")

        if len(command) < 2:
            raise ValueError("RPC command must contain ID and length")

        if len(command) > RPC_MAX_PACKET_LENGTH:
            raise ValueError( f"RPC command too large: {len(command)} bytes")

        command_id = command[0]
        command_length = command[1]

        actual_payload_length = len(command) - 2

        if command_length != actual_payload_length:
            raise ValueError(f"RPC command length mismatch: header={command_length}, actual={actual_payload_length}")

        async with self.command_lock:

            loop = asyncio.get_running_loop()

            # IMPORTANT:
            #
            # Create the Future BEFORE sending the command.
            #
            # The MCU could respond very quickly, so the response
            # notification could theoretically arrive immediately after
            # write_gatt_char() starts.
            self.response_future = loop.create_future()

            print()
            print( f"[RPC] Sending command ID=0x{command_id:02X}, Length={command_length}, Data={command.hex(' ')}" )

            start_time = time.perf_counter()

            try:

                # response=True means wait for the ATT write response.
                await self.client.write_gatt_char( self.command_uuid, command, response=True )

                # Now wait for the actual E002 notification.
                response = await asyncio.wait_for( asyncio.shield(self.response_future), timeout=timeout )

                end_time = time.perf_counter()

                response_time_ms = (end_time - start_time) * 1000.0

                print(f"[RPC] Response time: {response_time_ms:.3f} ms")

                return response

            except asyncio.TimeoutError:

                end_time = time.perf_counter()

                elapsed_ms = (end_time - start_time) * 1000.0

                print(f"[RPC] ERROR: response timeout after {elapsed_ms:.3f} ms")

                raise

            finally:
                self.response_future = None

    async def disconnect(self):

        if self.client is None:
            return

        try:

            if self.client.is_connected:

                print()
                print("Stopping RPC response notifications...")

                try:
                    await self.client.stop_notify(self.response_uuid)
                except Exception as exc:
                    print(f"Warning while stopping response notifications: {exc}")

                print("Stopping RPC asynchronous notifications...")

                try:
                    await self.client.stop_notify(self.notification_uuid)
                except Exception as exc:
                    print( f"Warning while stopping asynchronous notifications: {exc}" )

                print("Disconnecting...")

                await self.client.disconnect()

        finally:

            self.client = None

            print("Disconnected.")
